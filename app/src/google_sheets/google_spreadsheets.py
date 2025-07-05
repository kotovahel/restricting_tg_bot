import json
import logging

from google.oauth2 import service_account
from googleapiclient.discovery import build

import pandas as pd
from datetime import datetime

from app.src.utils import LOG_LEVEL

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


class ServiceAccount:

    def __init__(self, credentials, scopes, service_name, version):
        """Build the service using credentials file.

        :param credentials: str  Path to service account json file.
        :param scopes: list[str]  List of scopes.
        :param service_name: str  Name of the service.
        :param version: str  Version of the service.
        """

        # Load service account credentials
        self.credentials = service_account.Credentials.from_service_account_file(credentials)
        self.scopes = scopes

        # Build the service
        self.service = build(service_name, version, credentials=self.credentials)

    def read_spreadsheet(self, spreadsheet_id, range_name, header=True):
        """Read spreadsheet and return dataframe.

        :param spreadsheet_id: str  Spreadsheet ID. Can be retrieved from the URL.
        :param range_name: str  Range of the data. Example: 'A:B', 'Sheet1!A1:C60'
        :param header: bool  Whether to set header from the first row.
        :return: pd.DataFrame  Spreadsheet as a dataframe.
        """

        # Call the Sheets API to get the specified range of values
        result = self.service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()

        # Get the values from the response
        values = result.get('values', [])

        if not header:
            return pd.DataFrame(values)
        else:
            return pd.DataFrame(values[1:], columns=values[0])

    def write_spreadsheet(self, spreadsheet_id, df: pd.DataFrame, header=True):
        """Write the data to the spreadsheet

        :param spreadsheet_id: str  Spreadsheet ID. Can be retrieved from the URL.
        :param df: pd.DataFrame  Data to be written to the spreadsheet.
        :param header: bool  Whether to write header or not.
        :return:
        """
        # Prepare data to write to the spreadsheet
        values = json.loads(df.to_json(orient='values'))

        if header:
            values.insert(0, df.columns.values.tolist())

        # Write data to the spreadsheet
        body = {
            'values': values
        }

        range_ = 'A1'
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_,
            valueInputOption='RAW',
            body=body
        ).execute()
        logger.info('Data written to spreadsheet "{}".'.format(spreadsheet_id))

    def save_user_to_sheets(self, spreadsheet_id: int, users):
        """
        Save one or multiple users to spreadsheet.

        users: dict (one user) or list of dicts (multiple users).
        Each user dict should have keys: 'id', 'name', 'username' (optional).
        """

        prev_df = self.read_spreadsheet(spreadsheet_id, 'A:F')
        prev_df['id'] = prev_df['id'].astype(str)

        if isinstance(users, dict):
            users = [users]
        elif not isinstance(users, list):
            raise TypeError("users must be a dict or list of dicts")

        if not users:
            # No users to add — exit early
            return

        new_records = []
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for user in users:
            username = user.get("username") or ""
            new_records.append({
                "id": str(user["id"]),
                "name": user.get("name", ""),
                "username": username,
                "join_date": now_str,
                "deposit": 0,
                "restricted": 0
            })

        new_df = pd.DataFrame(new_records)
        new_df['id'] = new_df['id'].astype(str)

        ids_prev = set(prev_df['id'])
        filtered_new_df = new_df[~new_df['id'].isin(ids_prev)]

        if not filtered_new_df.empty:
            combined_df = pd.concat([prev_df, filtered_new_df], ignore_index=True)
            self.write_spreadsheet(spreadsheet_id, combined_df)

    def restrict_user(self, spreadsheet_id: str, username: str):
        prev_df = self.read_spreadsheet(spreadsheet_id, 'A:F')
        if not username:
            raise ValueError("Username cannot be empty")
        mask = prev_df['username'].str.lower() == username.lower()
        if not mask.any():
            raise ValueError(f"The user @{username} is not in the database")
        prev_df.loc[mask, 'restricted'] = 1
        self.write_spreadsheet(spreadsheet_id, prev_df)

    def get_restricted_user_ids(self, spreadsheet_id: str):
        df = self.read_spreadsheet(spreadsheet_id, 'A:F')
        df['deposit'] = df['deposit'].astype(float)
        df.loc[df['deposit'] > 0, 'restricted'] = '1'
        df['restricted'] = df['restricted'].astype(str)
        self.write_spreadsheet(spreadsheet_id, df)
        return set(df[df['restricted'] == '1']['id'].astype(int).tolist())





