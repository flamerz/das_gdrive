import os
from urllib.parse import quote

from apiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

import frappe
from frappe import _
from frappe.integrations.google_oauth import GoogleOAuth
from frappe.integrations.offsite_backup_utils import (
	get_latest_backup_file,
	send_email,
	validate_file_size,
)
from frappe.model.document import Document
from frappe.utils import get_backups_path, get_bench_path
from frappe.utils.background_jobs import enqueue
from frappe.utils.backups import new_backup
from frappe.integrations.doctype.google_drive.google_drive import get_google_drive_object, check_for_folder_in_google_drive, set_progress, get_absolute_path
@frappe.whitelist()
def take_backup():
	"""Enqueue longjob for taking backup to Google Drive"""
	enqueue(
		"das_gdrive.custom.gdrive.upload_system_backup_to_google_drive",
		queue="long",
		timeout=1500,
	)
	frappe.msgprint(_("Queued for backup. It may take a few minutes to an hour."))


def upload_system_backup_to_google_drive():
	"""
	Upload system backup to Google Drive
	"""
	# Get Google Drive Object
	google_drive, account = get_google_drive_object()

	# Check if folder exists in Google Drive
	check_for_folder_in_google_drive()
	account.load_from_db()

	validate_file_size()

	if frappe.flags.create_new_backup:
		set_progress(1, "Backing up Data.")
		backup = new_backup(ignore_files=True)
		file_urls = []
		file_urls.append(backup.backup_path_db)
		file_urls.append(backup.backup_path_conf)

		if account.file_backup:
			file_urls.append(backup.backup_path_files)
			file_urls.append(backup.backup_path_private_files)
	else:
		file_urls = get_latest_backup_file(with_files=account.file_backup)

	for fileurl in file_urls:
		if not fileurl:
			continue

		file_metadata = {"name": os.path.basename(fileurl), "parents": [account.backup_folder_id]}

		try:
			media = MediaFileUpload(
				get_absolute_path(filename=fileurl), mimetype="application/gzip", resumable=True
			)
		except OSError as e:
			frappe.throw(_("Google Drive - Could not locate - {0}").format(e))

		try:
			set_progress(2, "Uploading backup to Google Drive.")
			google_drive.files().create(body=file_metadata, media_body=media, fields="id").execute()
		except HttpError as e:
			send_email(False, "Google Drive", "Google Drive", "email", error_status=e)

	set_progress(3, "Uploading successful.")
	frappe.db.set_single_value("Google Drive", "last_backup_on", frappe.utils.now_datetime())
	send_email(True, "Google Drive", "Google Drive", "email")
	return _("Google Drive Backup Successful.")