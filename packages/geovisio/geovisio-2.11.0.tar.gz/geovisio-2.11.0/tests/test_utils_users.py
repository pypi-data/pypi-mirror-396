from .conftest import (
    insert_db_model,
    ModelToInsert,
    UploadSetToInsert,
    SequenceToInsert,
    PictureToInsert,
)
from geovisio.utils import users, db
from geovisio.utils.auth import Account
from psycopg.rows import dict_row


def test_user_data_deletion(app, bobAccountID, camilleAccountID):
    accounts = {"bob": bobAccountID, "camille": camilleAccountID}
    with app.app_context(), app.test_client() as client:
        insert_db_model(
            ModelToInsert(
                upload_sets=[
                    UploadSetToInsert(
                        sequences=[
                            SequenceToInsert(
                                title=f"sequence_{i}_of_{account_name}",
                                pictures=[
                                    PictureToInsert(original_file_name=f"{i}_1.jpg"),
                                    PictureToInsert(original_file_name=f"{i}_2.jpg"),
                                    PictureToInsert(original_file_name=f"{i}_3.jpg"),
                                ],
                            ),
                            SequenceToInsert(
                                title=f"sequence_empty_{i}_of_{account_name}",
                            ),
                        ],
                        account_id=account_id,
                        title=f"upload_{i}_of_{account_name}",
                    )
                    for account_name, account_id in accounts.items()
                    for i in range(1, 3)
                ]
                + [UploadSetToInsert(sequences=[], account_id=camilleAccountID, title="empty us from camille")],
            )
        )

        def res_to_map(rows):

            return {r["key"]: r["nb"] for r in rows}

        with db.conn(app) as conn, conn.cursor(row_factory=dict_row) as cursor:
            # we get the stats before deleting the user data
            nb_pics_by_users = cursor.execute("SELECT account_id as key, COUNT(*) AS nb FROM pictures group by account_id").fetchall()
            assert res_to_map(nb_pics_by_users) == {bobAccountID: 6, camilleAccountID: 6}
            nb_us_by_users = cursor.execute("SELECT account_id as key, COUNT(*) AS nb FROM upload_sets group by account_id").fetchall()
            assert res_to_map(nb_us_by_users) == {bobAccountID: 2, camilleAccountID: 3}
            nb_seqs_by_users = cursor.execute("SELECT account_id as key, COUNT(*) AS nb FROM sequences group by account_id").fetchall()
            assert res_to_map(nb_seqs_by_users) == {bobAccountID: 4, camilleAccountID: 4}
            nb_tasks = cursor.execute(
                """SELECT
                CASE 
                    WHEN picture_id IS NOT NULL THEN CONCAT(task, '_on_pic') 
                    WHEN sequence_id IS NOT NULL THEN CONCAT(task, 'on_seq')
                    WHEN upload_set_id IS NOT NULL THEN CONCAT(task, '_on_us')
                    WHEN picture_to_delete_id IS NOT NULL THEN CONCAT(task, '_on_pic_to_delete')
                    
                    ELSE CONCAT(task, '_')
                END as key,
                count(*) AS nb 
                FROM job_queue group by 1"""
            ).fetchall()
            assert res_to_map(nb_tasks) == {"prepare_on_pic": 12}

            users.delete_user_data(conn, Account(id=camilleAccountID, name="camille"))

            # check that all has been deleted, and that the async tasks have been added
            nb_pics_by_users = cursor.execute("SELECT account_id as key, COUNT(*) AS nb FROM pictures group by account_id").fetchall()
            assert res_to_map(nb_pics_by_users) == {bobAccountID: 6}
            nb_us_by_users = cursor.execute("SELECT account_id as key, COUNT(*) AS nb FROM upload_sets group by account_id").fetchall()
            assert res_to_map(nb_us_by_users) == {bobAccountID: 2}
            nb_seqs_by_users = cursor.execute("SELECT account_id as key, COUNT(*) AS nb FROM sequences group by account_id").fetchall()
            assert res_to_map(nb_seqs_by_users) == {bobAccountID: 4, camilleAccountID: 4}
            nb_seqs_by_users = cursor.execute(
                "SELECT status as key, COUNT(*) AS nb FROM sequences where account_id = %s group by status", [camilleAccountID]
            ).fetchall()
            assert res_to_map(nb_seqs_by_users) == {"deleted": 4}
            nb_tasks = cursor.execute(
                """SELECT
                CASE 
                    WHEN picture_id IS NOT NULL THEN CONCAT(task, '_on_pic') 
                    WHEN sequence_id IS NOT NULL THEN CONCAT(task, 'on_seq')
                    WHEN upload_set_id IS NOT NULL THEN CONCAT(task, '_on_us')
                    WHEN picture_to_delete_id IS NOT NULL THEN CONCAT(task, '_on_pic_to_delete')
                    
                    ELSE CONCAT(task, '_')
                END as key,
                count(*) AS nb 
                FROM job_queue group by 1"""
            ).fetchall()
            assert res_to_map(nb_tasks) == {
                "delete_on_pic_to_delete": 6,
                "prepare_on_pic": 6,  # we do not need to prepare the deleted pictures
            }
