import logging
from geovisio.utils.auth import Account


def delete_user_data(conn, account: Account):
    """Delete all the pictures of a user

    Note that the database changes will be done synchronously but the picture deletion will be an asynchronous task,
    so some background workers need to be run in order for the pictures deletion to be effective.
    """
    with conn.transaction(), conn.cursor() as cursor:
        logging.info(f"Deleting pictures of account {account.name} ({account.id})")
        # Note: deleting a picture's row add a new `delete` async task to the queue, to delete the associated files
        nb_deleted_pics = cursor.execute("DELETE FROM pictures WHERE account_id = %s", [account.id]).rowcount
        cursor.execute("DELETE FROM upload_sets WHERE account_id = %s", [account.id])
        cursor.execute("UPDATE sequences SET status = 'deleted' WHERE account_id = %s", [account.id])
        logging.info(f"Deleted {nb_deleted_pics} pictures from account {account.name} ({account.id})")
        return nb_deleted_pics
