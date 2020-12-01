from src.report_generator import report_generation
from datetime import timedelta
import pandas as pd
import requests


def transform_info(all_category_cols):
    transformed_info = []
    for local_col in all_category_cols:
        x = [x['category'] for x in local_col['data']]
        y = [x['frequency'] for x in local_col['data']]
        new_dict = {'col_name': local_col['col_name'],
                    'x': x,
                    'y': y}
        transformed_info.append(new_dict)
    return transformed_info


def query_monday(query, api_key):
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization": api_key}
    data = {'query': query}
    r = requests.post(url=apiUrl, json=data, headers=headers)
    response = r.json()
    return response


def get_relevant_boards(api_key):
    query_boards = '''query{
                    boards {
                    id
                    name
                    updated_at
                    workspace {name}
                        }
                    }
                    '''
    boards_response = query_monday(query_boards, api_key)
    boards_list = boards_response['data']['boards']
    boards_df = pd.DataFrame(boards_list)
    boards_df['updated_at'] = pd.to_datetime(boards_df['updated_at'])
    boards_df['workspace'] = boards_df['workspace'].apply(lambda x: x['name'])
    # last 7 days calculation
    today = pd.Timestamp.utcnow()
    last_week = today - timedelta(days=7)
    # filter relevant updates
    relevant_boards = boards_df.query(f"updated_at >= '{last_week}'")
    return relevant_boards


def query_boad_info(board_id, api_key):
    '''
    Query info for single board.
    '''
    query_boards_info = "query{" \
        f"boards (ids: {board_id})" \
        """{
                name
                workspace {name}
                owner {name}
                items {name, id}
                columns {type, id, title}
                updated_at
                    }
                }
                """
    boards_info_response = query_monday(query_boards_info.replace('\n', ''), api_key)
    boards_info_summary = boards_info_response['data']['boards'][0]
    return boards_info_summary


def query_items(items_ids_str, api_key):
    '''
    Params:
        items_ids_str - List of ids.
        i.e.  items_ids_str = [850688875, 850688872]
    '''
    query_items_info = "query {" \
        f"items (ids: {items_ids_str})" \
        """  {
                            name
                            column_values {id, text}
                                }
                            }
                            """
    items_info_response = query_monday(query_items_info.replace('\n', ''), api_key)
    items_info_summary = items_info_response['data']['items']
    return items_info_summary


def get_users_info(items_info_summary, type_ids_list):
    '''
    Uses items(rows) query and column-type data to retrieve
    the name of the users present in the board


    To do:

    '''
    rows_count = len(items_info_summary)
    cols_count = len(items_info_summary[0]['column_values'])

    monstert_list = [ele['column_values'] for ele in items_info_summary]
    flat_list = [item for sublist in monstert_list for item in sublist]
    rows_content = pd.DataFrame(flat_list)

    persons_in_project = rows_content.query(f"id.isin({type_ids_list})")
    persons_count = persons_in_project.text.value_counts()
    persons_count_df = persons_count.reset_index()
    persons_count_df.rename(columns={"index": "user_name", "text": "user_count"},
                            inplace=True)
    persons_count_df['user_name'] = persons_count_df['user_name'].apply(
        lambda x: 'Unassigned' if x == '' else x)
    persons_count_dict = persons_count_df.to_dict(orient='records')

    users_info_response = {'board_tasks_count': rows_count,
                           'board_columns_count': cols_count,
                           'users_workload': persons_count_dict}
    return users_info_response


def get_user_activity(board_id, board_name, api_key):
    boards_info_summary = query_boad_info(board_id, api_key)

    type_ids_df = pd.DataFrame(boards_info_summary['columns']).query("type == 'multiple-person'")
    type_ids_list = type_ids_df['id'].to_list()

    items_df = pd.DataFrame(boards_info_summary['items'])
    items_ids_list = items_df['id'].to_list()
    items_ids_str = str(items_ids_list).replace("'", '')

    items_info_summary = query_items(items_ids_str, api_key)
    users_info_response = get_users_info(items_info_summary, type_ids_list)
    users_info_response['board_name'] = board_name
    return users_info_response


def get_board_categories(board_id, api_key):
    boards_info_summary = query_boad_info(board_id, api_key)
    color_type_ids_df = pd.DataFrame(boards_info_summary['columns']).query("type == 'color'")
    color_type_ids_list = color_type_ids_df.to_dict(orient='records')
    items_df = pd.DataFrame(boards_info_summary['items'])
    items_ids_list = items_df['id'].to_list()
    items_ids_str = str(items_ids_list).replace("'", '')
    items_info_summary = query_items(items_ids_str, api_key)

    monster_list = [ele['column_values'] for ele in items_info_summary]
    flat_list = [item for sublist in monster_list for item in sublist]
    rows_content = pd.DataFrame(flat_list)

    all_category_cols = []
    for category_ele in color_type_ids_list:
        category_col = category_ele.get('id')
        col_name = category_ele.get('title')
        persons_in_project = rows_content.query(f"id.isin(['{category_col}'])")
        persons_count = persons_in_project.text.value_counts()
        persons_count_df = persons_count.reset_index()
        persons_count_df.rename(columns={"index": "category", "text": "frequency"},
                                inplace=True)
        persons_count_dict = persons_count_df.to_dict(orient='records')
        col_dic = {'col_name': col_name,
                   'data': persons_count_dict}
        all_category_cols.append(col_dic)
    return all_category_cols


# BOARD LEVEL INFO

def get_board_output_data(relevant_boards_dict, api_key):
    '''
    Input:
        - relevant_boards_dict: dict with ids of all the boards
                                belonging to a workspace.
    '''
    board_output_data = []
    for board_dict in relevant_boards_dict:
        board_id = board_dict.get('id')
        board_name = board_dict.get('name')
        print(f"\nGetting board: {board_name}")
        all_category_cols = get_board_categories(board_id, api_key)
        transformed_info = transform_info(all_category_cols)
        board_output = {'board': board_name,
                        'columns': transformed_info}
        board_output_data.append(board_output)
    return board_output_data


def get_user_board_info(relevant_boards_dict, api_key):
    all_users_boards = []
    for user_board in relevant_boards_dict:
        board_id = user_board.get('id')
        board_name = user_board.get('name')
        users_info_response = get_user_activity(board_id, board_name, api_key)
        all_users_boards.append(users_info_response)
    return all_users_boards


def get_all_workspace_info(relevant_boards, api_key, mode='column_types'):
    '''
    relevant_boards is obtained with func 'get_relevant_boards'
    '''
    workspaces_list = relevant_boards.workspace.unique()
    workspaces_info = []
    for workspace in workspaces_list:
        print(f"\nGettint workspace: {workspace}")
        local_workspace = relevant_boards.query(f"workspace == '{workspace}'")
        relevant_boards_dict = local_workspace.to_dict(orient='records')
        if mode == 'column_types':
            board_output_data = get_board_output_data(relevant_boards_dict, api_key)
        else:
            board_output_data = get_user_board_info(relevant_boards_dict, api_key)
        local_workspace_dict = {'workspace': workspace,
                                'workspace_data': board_output_data
                                }
        workspaces_info.append(local_workspace_dict)
    return workspaces_info


def monday_admin_info(input_):
    '''
    Function that connects to Monday.com through an API Key
    and retrieves info from the boards updated during the
    last 7 days.
    ''' 
    api_key = input_
    print("Getting info for report...")
    relevant_boards = get_relevant_boards(api_key)
    print("\n\nGetting active users...")
    users_main = get_all_workspace_info(relevant_boards, api_key, mode='users')
    print("\n\nGetting active boards...")
    work_main = get_all_workspace_info(relevant_boards, api_key)
    print("\n\nProcess completed correctly!")
    week_summary = {'users_info': users_main,
                    'work_info': work_main
                    }
    return week_summary
