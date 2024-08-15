# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__version__ = '0.0.1'

from frappe.integrations.doctype.google_drive import google_drive

from das_gdrive.custom.gdrive import upload_system_backup_to_google_drive

google_drive.upload_system_backup_to_google_drive = upload_system_backup_to_google_drive