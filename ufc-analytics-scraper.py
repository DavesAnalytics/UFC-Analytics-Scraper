!pip install requests
!pip install beautifulsoup4
!pip install pandas

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time as sleeptime
import sys
from difflib import get_close_matches
import numpy as np

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

def search_fighter_by_name_part(query):
    url = "http://ufcstats.com/statistics/fighters/search"
    params = {"query": query}
    response = requests.get(url, params=params)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', class_='b-statistics__table')
    if not table:
        return []
    rows = table.find('tbody').find_all('tr', class_='b-statistics__table-row')
    candidates = []
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 2:
            continue
        first_name_col = cols[0].find('a', class_='b-link_style_black')
        last_name_col = cols[1].find('a', class_='b-link_style_black')
        if not first_name_col or not last_name_col:
            continue
        first_name = first_name_col.get_text(strip=True)
        last_name = last_name_col.get_text(strip=True)
        fighter_link = last_name_col['href']
        full_name = f"{first_name} {last_name}".strip()
        candidates.append((full_name, fighter_link))
    return candidates

def get_fighter_url_by_name(fighter_name):
    print(f"\nAttempting to find URL for fighter: {fighter_name}")
    name_parts = fighter_name.strip().split()
    fighter_name_clean = fighter_name.strip().lower()

    if len(name_parts) > 1:
        last_name = name_parts[-1]
        first_name = name_parts[0]
        candidates = search_fighter_by_name_part(last_name)
        if not candidates:
            candidates = search_fighter_by_name_part(first_name)
        if not candidates:
            for part in name_parts:
                candidates = search_fighter_by_name_part(part)
                if candidates:
                    break
        if not candidates:
            raise ValueError(f"No suitable match found for fighter: {fighter_name_clean}")
        all_names = [c[0].lower() for c in candidates]
        close = get_close_matches(fighter_name_clean, all_names, n=1, cutoff=0.0)
        if close:
            best = close[0]
            for c in candidates:
                if c[0].lower() == best:
                    return c[1]
            return candidates[0][1]
        else:
            return candidates[0][1]
    else:
        query = name_parts[0]
        candidates = search_fighter_by_name_part(query)
        if not candidates:
            raise ValueError(f"No suitable match found for fighter: {fighter_name_clean}")
        all_names = [c[0].lower() for c in candidates]
        close = get_close_matches(fighter_name_clean, all_names, n=1, cutoff=0.0)
        if close:
            best = close[0]
            for c in candidates:
                if c[0].lower() == best:
                    return c[1]
            return candidates[0][1]
        else:
            return candidates[0][1]

def get_two_values_from_col(col):
    ps = col.find_all('p', class_='b-fight-details__table-text')
    if len(ps) == 2:
        return ps[0].get_text(strip=True), ps[1].get_text(strip=True)
    return None, None

def ctrl_to_seconds(x):
    if x and ':' in x:
        m,s = x.split(':')
        if m.isdigit() and s.isdigit():
            return str(int(m)*60 + int(s))
    return x

def get_fight_links(fighter_url):
    response = requests.get(fighter_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    table = soup.find('table', class_='b-fight-details__table_type_event-details')
    if not table:
        raise Exception("No fight details table found on the fighter page.")
    
    rows = table.find('tbody').find_all('tr', class_='b-fight-details__table-row__hover')
    fights_data = []
    
    for row in rows:
        fight_url = row.get('data-link')
        if not fight_url:
            continue
        
        cols = row.find_all('td', class_='b-fight-details__table-col')
        result_tag = cols[0].find('p', class_='b-fight-details__table-text')
        result = result_tag.get_text(strip=True) if result_tag else None

        fighter_td = cols[1].find_all('p', class_='b-fight-details__table-text')
        fighter_name = fighter_td[0].get_text(strip=True) if len(fighter_td) > 0 else None
        opponent_name = fighter_td[1].get_text(strip=True) if len(fighter_td) > 1 else None

        kd_fighter, kd_opponent = get_two_values_from_col(cols[2])
        str_fighter, str_opponent = get_two_values_from_col(cols[3])
        td_fighter, td_opponent = get_two_values_from_col(cols[4])
        sub_fighter, sub_opponent = get_two_values_from_col(cols[5])

        event_td = cols[6].find_all('p', class_='b-fight-details__table-text')
        event_name = event_td[0].get_text(strip=True) if len(event_td) > 0 else None
        event_date = event_td[1].get_text(strip=True) if len(event_td) > 1 else None

        method_td = cols[7].find_all('p', class_='b-fight-details__table-text')
        method_main = method_td[0].get_text(strip=True) if len(method_td) > 0 else None
        method_detail = method_td[1].get_text(strip=True) if len(method_td) > 1 else None

        round_val = cols[8].find('p', class_='b-fight-details__table-text')
        round_val = round_val.get_text(strip=True) if round_val else None

        time_val = cols[9].find('p', class_='b-fight-details__table-text')
        time_val = time_val.get_text(strip=True) if time_val else None

        # Convert time_val to seconds if mm:ss
        if time_val and ':' in time_val:
            parts = time_val.split(':')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                mm, ss = parts
                total_sec = int(mm)*60 + int(ss)
                time_val = str(total_sec)

        fight_data = {
            'result': result,
            'fighter_name': fighter_name,
            'opponent_name': opponent_name,
            'kd_fighter': kd_fighter,
            'kd_opponent': kd_opponent,
            'str_fighter': str_fighter,
            'str_opponent': str_opponent,
            'td_fighter': td_fighter,
            'td_opponent': td_opponent,
            'sub_fighter': sub_fighter,
            'sub_opponent': sub_opponent,
            'event_name': event_name,
            'event_date': event_date,
            'method_main': method_main,
            'method_detail': method_detail,
            'round': round_val,
            'Time': time_val,
            'fight_link': fight_url
        }
        
        fights_data.append(fight_data)
    links = [f['fight_link'] for f in fights_data]
    return links, pd.DataFrame(fights_data)

def parse_totals_table(soup, main_fighter_name):
    totals_heading = soup.find('p', class_='b-fight-details__collapse-link_tot', string=lambda x: x and 'Totals' in x)
    if not totals_heading:
        return {}
    totals_section = totals_heading.find_next('section', class_='b-fight-details__section')
    if not totals_section:
        return {}
    totals_table = totals_section.find('table')
    if not totals_table:
        return {}
    
    rows = totals_table.find('tbody').find_all('tr', class_='b-fight-details__table-row')
    if len(rows) == 0:
        return {}

    def get_two_val(cell):
        ps = cell.find_all('p', class_='b-fight-details__table-text')
        if len(ps) == 2:
            return ps[0].get_text(strip=True), ps[1].get_text(strip=True)
        return None, None

    first_row = rows[0]
    cols = first_row.find_all('td')
    if len(cols) < 10:
        return {}

    fighter_col = cols[0]
    fighter1, fighter2 = get_two_val(fighter_col)
    if fighter1 is None or fighter2 is None:
        return {}

    main_is_first = (main_fighter_name.lower() == fighter1.lower())

    kd_f1, kd_f2 = get_two_val(cols[1])
    str_f1, str_f2 = get_two_val(cols[2])
    str_pct_f1, str_pct_f2 = get_two_val(cols[3])
    total_str_f1, total_str_f2 = get_two_val(cols[4])
    td_f1, td_f2 = get_two_val(cols[5])
    td_pct_f1, td_pct_f2 = get_two_val(cols[6])
    sub_f1, sub_f2 = get_two_val(cols[7])
    rev_f1, rev_f2 = get_two_val(cols[8])
    ctrl_f1, ctrl_f2 = get_two_val(cols[9])

    ctrl_f1 = ctrl_to_seconds(ctrl_f1)
    ctrl_f2 = ctrl_to_seconds(ctrl_f2)

    data = {}
    if main_is_first:
        data['TOT_fighter_KD'] = kd_f1
        data['TOT_opponent_KD'] = kd_f2
        data['TOT_fighter_SigStr'] = str_f1
        data['TOT_opponent_SigStr'] = str_f2
        data['TOT_fighter_SigStr_pct'] = str_pct_f1
        data['TOT_opponent_SigStr_pct'] = str_pct_f2
        data['TOT_fighter_Str'] = total_str_f1
        data['TOT_opponent_Str'] = total_str_f2
        data['TOT_fighter_Td'] = td_f1
        data['TOT_opponent_Td'] = td_f2
        data['TOT_fighter_Td_pct'] = td_pct_f1
        data['TOT_opponent_Td_pct'] = td_pct_f2
        data['TOT_fighter_SubAtt'] = sub_f1
        data['TOT_opponent_SubAtt'] = sub_f2
        data['TOT_fighter_Rev'] = rev_f1
        data['TOT_opponent_Rev'] = rev_f2
        data['TOT_fighter_Ctrl'] = ctrl_f1
        data['TOT_opponent_Ctrl'] = ctrl_f2
    else:
        data['TOT_fighter_KD'] = kd_f2
        data['TOT_opponent_KD'] = kd_f1
        data['TOT_fighter_SigStr'] = str_f2
        data['TOT_opponent_SigStr'] = str_f1
        data['TOT_fighter_SigStr_pct'] = str_pct_f2
        data['TOT_opponent_SigStr_pct'] = str_pct_f1
        data['TOT_fighter_Str'] = total_str_f2
        data['TOT_opponent_Str'] = total_str_f1
        data['TOT_fighter_Td'] = td_f2
        data['TOT_opponent_Td'] = td_f1
        data['TOT_fighter_Td_pct'] = td_pct_f2
        data['TOT_opponent_Td_pct'] = td_pct_f1
        data['TOT_fighter_SubAtt'] = sub_f2
        data['TOT_opponent_SubAtt'] = sub_f1
        data['TOT_fighter_Rev'] = rev_f2
        data['TOT_opponent_Rev'] = rev_f1
        data['TOT_fighter_Ctrl'] = ctrl_f2
        data['TOT_opponent_Ctrl'] = ctrl_f1

    return data

def parse_per_round_totals(soup, main_fighter_name):
    totals_heading = soup.find('p', class_='b-fight-details__collapse-link_tot', string=lambda x: x and 'Totals' in x)
    if not totals_heading:
        return {}
    per_round_link = totals_heading.find_next('a', class_='b-fight-details__collapse-link_rnd', string=lambda x: x and 'Per round' in x)
    if not per_round_link:
        return {}
    per_round_table = per_round_link.find_next('table', class_='b-fight-details__table')
    if not per_round_table:
        return {}

    def get_two_vals_from_cell(cell):
        ps = cell.find_all('p', class_='b-fight-details__table-text')
        if len(ps) == 2:
            return ps[0].get_text(strip=True), ps[1].get_text(strip=True)
        return None, None

    round_headers = per_round_table.find_all('thead', class_='b-fight-details__table-row_type_head')
    if not round_headers:
        return {}
    first_header = round_headers[0]
    first_data_row = first_header.find_next('tr', class_='b-fight-details__table-row')
    if not first_data_row:
        return {}
    first_cells = first_data_row.find_all('td', class_='b-fight-details__table-col')
    if len(first_cells) < 9:
        return {}

    first_f1_name, first_f2_name = get_two_vals_from_cell(first_cells[0])
    if not first_f1_name or first_f2_name is None:
        return {}

    main_is_first = (main_fighter_name.lower() == first_f1_name.lower())

    data = {}
    for rh in round_headers:
        round_name = rh.get_text(strip=True).replace('Round ', '')
        data_row = rh.find_next('tr', class_='b-fight-details__table-row')
        if not data_row:
            continue
        cells = data_row.find_all('td', class_='b-fight-details__table-col')
        if len(cells) < 9:
            continue

        kd = get_two_vals_from_cell(cells[1])
        sig_str = get_two_vals_from_cell(cells[2])
        sig_str_pct = get_two_vals_from_cell(cells[3])
        total_str = get_two_vals_from_cell(cells[4])
        td_pct = get_two_vals_from_cell(cells[5])
        sub_att = get_two_vals_from_cell(cells[6])
        rev = get_two_vals_from_cell(cells[7])
        ctrl = get_two_vals_from_cell(cells[8])

        if ctrl is not None:
            ctrl_f1, ctrl_f2 = ctrl
            ctrl_f1 = ctrl_to_seconds(ctrl_f1)
            ctrl_f2 = ctrl_to_seconds(ctrl_f2)
        else:
            ctrl_f1, ctrl_f2 = None, None

        def assign_vals(val_pair):
            if val_pair is None:
                return None, None
            v1, v2 = val_pair
            return (v1, v2) if main_is_first else (v2, v1)

        kd_fighter, kd_opponent = assign_vals(kd)
        sigstr_fighter, sigstr_opponent = assign_vals(sig_str)
        sigstrpct_fighter, sigstrpct_opponent = assign_vals(sig_str_pct)
        str_fighter, str_opponent = assign_vals(total_str)
        tdpct_fighter, tdpct_opponent = assign_vals(td_pct)
        subatt_fighter, subatt_opponent = assign_vals(sub_att)
        rev_fighter, rev_opponent = assign_vals(rev)
        ctrl_fighter, ctrl_opponent = (ctrl_f1, ctrl_f2) if main_is_first else (ctrl_f2, ctrl_f1)

        data[f'Round{round_name}_fighter_KD'] = kd_fighter
        data[f'Round{round_name}_opponent_KD'] = kd_opponent
        data[f'Round{round_name}_fighter_SigStr'] = sigstr_fighter
        data[f'Round{round_name}_opponent_SigStr'] = sigstr_opponent
        data[f'Round{round_name}_fighter_SigStr_pct'] = sigstrpct_fighter
        data[f'Round{round_name}_opponent_SigStr_pct'] = sigstrpct_opponent
        data[f'Round{round_name}_fighter_Str'] = str_fighter
        data[f'Round{round_name}_opponent_Str'] = str_opponent
        data[f'Round{round_name}_fighter_Td_pct'] = tdpct_fighter
        data[f'Round{round_name}_opponent_Td_pct'] = tdpct_opponent
        data[f'Round{round_name}_fighter_SubAtt'] = subatt_fighter
        data[f'Round{round_name}_opponent_SubAtt'] = subatt_opponent
        data[f'Round{round_name}_fighter_Rev'] = rev_fighter
        data[f'Round{round_name}_opponent_Rev'] = rev_opponent
        data[f'Round{round_name}_fighter_Ctrl'] = ctrl_fighter
        data[f'Round{round_name}_opponent_Ctrl'] = ctrl_opponent

    return data

def parse_per_round_significant_strikes(soup, main_fighter_name):
    sections = soup.find_all('section', class_='b-fight-details__section')
    sig_strikes_section = None
    for s in sections:
        heading = s.find('p', class_='b-fight-details__collapse-link_tot')
        if heading and 'Significant Strikes' in heading.get_text():
            sig_strikes_section = s
            break
    
    if not sig_strikes_section:
        return {}
    
    start_index = sections.index(sig_strikes_section)
    per_round_table = None
    for s in sections[start_index:]:
        link = s.find('a', class_='b-fight-details__collapse-link_rnd')
        if link and 'Per round' in link.get_text():
            candidate_table = s.find('table', class_='b-fight-details__table')
            if candidate_table:
                per_round_table = candidate_table
                break
    
    if not per_round_table:
        return {}
    
    col_map = {
        1: 'SIG_STR',
        2: 'SIG_STR_PCT',
        3: 'HEAD',
        4: 'BODY',
        5: 'LEG',
        6: 'DISTANCE',
        7: 'CLINCH',
        8: 'GROUND'
    }

    def get_two_vals_from_cell(cell):
        ps = cell.find_all('p', class_='b-fight-details__table-text')
        if len(ps) == 2:
            return ps[0].get_text(strip=True), ps[1].get_text(strip=True)
        return None, None

    round_headers = per_round_table.find_all('thead', class_='b-fight-details__table-row_type_head')
    if not round_headers:
        return {}
    first_header = round_headers[0]
    first_data_row = first_header.find_next('tr', class_='b-fight-details__table-row')
    if not first_data_row:
        return {}
    first_cells = first_data_row.find_all('td', class_='b-fight-details__table-col')
    if len(first_cells) < 9:
        return {}
    
    first_f1_name, first_f2_name = get_two_vals_from_cell(first_cells[0])
    if not first_f1_name or first_f2_name is None:
        return {}
    
    main_is_first = (main_fighter_name.lower() == first_f1_name.lower())

    data = {}
    for rh in round_headers:
        round_name = rh.get_text(strip=True).replace('Round ', '')
        data_row = rh.find_next('tr', class_='b-fight-details__table-row')
        if not data_row:
            continue
        cells = data_row.find_all('td', class_='b-fight-details__table-col')
        if len(cells) < 9:
            continue

        for cidx, key in col_map.items():
            val1, val2 = get_two_vals_from_cell(cells[cidx])
            if main_is_first:
                data[f'Round{round_name}_fighter_{key}'] = val1
                data[f'Round{round_name}_opponent_{key}'] = val2
            else:
                data[f'Round{round_name}_fighter_{key}'] = val2
                data[f'Round{round_name}_opponent_{key}'] = val1

    return data

def parse_fight_details(fight_url, main_fighter_name, opponent_name):
    response = requests.get(fight_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    fight_data = {}
    event_title = soup.find('h2', class_='b-content__title')
    fight_data['Event'] = event_title.get_text(strip=True) if event_title else None

    fight_info = soup.find('div', class_='b-fight-details__fight')
    if fight_info:
        text_blocks = fight_info.find_all('p', class_='b-fight-details__text')
        for block in text_blocks:
            text = block.get_text(" ", strip=True)
            if 'Method:' in text:
                part = text.split('Method:')[1].split('Round:')[0].strip()
                fight_data['method_main'] = part
            if 'Round:' in text:
                part = text.split('Round:')[1].split('Time:')[0].strip()
                fight_data['round'] = part
            if 'Time:' in text:
                part = text.split('Time:')[1].split('Time format:')[0].strip()
                if ':' in part and all(x.isdigit() for x in part.split(':')):
                    mm, ss = part.split(':')
                    total_sec = int(mm)*60 + int(ss)
                    fight_data['Time'] = str(total_sec)
                else:
                    fight_data['Time'] = part
            if 'Time format:' in text:
                part = text.split('Time format:')[1]
                if 'Referee:' in part:
                    part = part.split('Referee:')[0].strip()
                else:
                    part = part.strip()
                fight_data['TimeFormat'] = part
            if 'Referee:' in text:
                part = text.split('Referee:')[1].strip()
                fight_data['Referee'] = part
            if 'Details:' in text:
                part = text.split('Details:')[1].strip()
                fight_data['Details'] = part

    totals_data = parse_totals_table(soup, main_fighter_name)
    if totals_data:
        fight_data.update(totals_data)

    per_round_totals_data = parse_per_round_totals(soup, main_fighter_name)
    if per_round_totals_data:
        fight_data.update(per_round_totals_data)

    round_data = parse_per_round_significant_strikes(soup, main_fighter_name)
    if round_data:
        fight_data.update(round_data)

    fight_data['fight_link'] = fight_url
    return fight_data

def transform_columns(df):
    # Replace '---' with NaN
    df.replace('---', np.nan, inplace=True)

    # Handle round and Time
    if 'round_x' in df.columns and 'round_y' in df.columns:
        df['round'] = df['round_y'].combine_first(df['round_x'])
        df.drop(columns=['round_x','round_y'], inplace=True)
    if 'Time_x' in df.columns and 'Time_y' in df.columns:
        df['Time'] = df['Time_y'].combine_first(df['Time_x'])
        df.drop(columns=['Time_x','Time_y'], inplace=True)

    # Handle method_main and method_detail
    # If both _x and _y exist, combine. If only one exists, rename it.
    if 'method_main_x' in df.columns and 'method_main_y' in df.columns:
        df['method_main'] = df['method_main_y'].combine_first(df['method_main_x'])
        df.drop(columns=['method_main_x','method_main_y'], inplace=True, errors='ignore')
    elif 'method_main_x' in df.columns:
        df.rename(columns={'method_main_x':'method_main'}, inplace=True)
    elif 'method_main_y' in df.columns:
        df.rename(columns={'method_main_y':'method_main'}, inplace=True)

    if 'method_detail_x' in df.columns and 'method_detail_y' in df.columns:
        df['method_detail'] = df['method_detail_y'].combine_first(df['method_detail_x'])
        df.drop(columns=['method_detail_x','method_detail_y'], inplace=True, errors='ignore')
    elif 'method_detail_x' in df.columns:
        df.rename(columns={'method_detail_x':'method_detail'}, inplace=True)
    elif 'method_detail_y' in df.columns:
        df.rename(columns={'method_detail_y':'method_detail'}, inplace=True)

    # Handle " of " columns
    df = df.astype(str)
    of_cols = [col for col in df.columns if df[col].str.contains(' of ', na=False).any()]

    new_cols = {}
    for col in of_cols:
        split_values = df[col].str.split(' of ', expand=True)
        new_landed_col = col + '_landed'
        new_attempted_col = col + '_attempted'
        new_percentage_col = col + '_percentage'

        landed = pd.to_numeric(split_values[0], errors='coerce')
        attempted = pd.to_numeric(split_values[1], errors='coerce')
        percentage = (landed / attempted) * 100
        percentage = percentage.round(2)

        new_cols[new_landed_col] = landed.astype(str)
        new_cols[new_attempted_col] = attempted.astype(str)
        new_cols[new_percentage_col] = percentage.astype(str)

    if of_cols:
        df.drop(columns=of_cols, inplace=True)

    if new_cols:
        df = pd.concat([df, pd.DataFrame(new_cols)], axis=1)

    # Remove '%' from percentage columns
    for col in df.columns:
        if df[col].str.endswith('%', na=False).any():
            df[col] = df[col].str.replace('%', '', regex=False)

    # Convert numeric columns if possible
    textual_cols = ['fighter_name','opponent_name','event_name','event_date',
                    'method_main','method_detail','Details','Referee','Event','TimeFormat',
                    'result','fight_link','round']
    for col in df.columns:
        if col not in textual_cols:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except:
                pass

    # Round all float columns to 2 decimals
    float_cols = df.select_dtypes(include=['float64','float32','float'])
    if not float_cols.empty:
        df[float_cols.columns] = float_cols.round(2)

    return df

# ---- MAIN EXECUTION ----
fighter_input_name = "Israel Adesanya"
try:
    fighter_url = get_fighter_url_by_name(fighter_input_name)
    print(f"Found URL for {fighter_input_name}: {fighter_url}")
except ValueError as e:
    print(e)
    sys.exit(1)

fight_links, main_fights_df = get_fight_links(fighter_url)

all_fight_details = []
for fl in fight_links:
    sleeptime.sleep(1)
    row = main_fights_df.loc[main_fights_df['fight_link'] == fl].iloc[0]
    main_fighter_name = row['fighter_name']
    opp_name = row['opponent_name']
    details = parse_fight_details(fl, main_fighter_name, opp_name)
    all_fight_details.append(details)

advanced_df = pd.DataFrame(all_fight_details)
combined_df = pd.merge(main_fights_df, advanced_df, on='fight_link', how='left')

combined_df = transform_columns(combined_df)

fighter_name_value = combined_df['fighter_name'].iloc[0]
if isinstance(fighter_name_value, float):
    fighter_name_for_filename = "Unknown_Fighter"
else:
    fighter_name_for_filename = str(fighter_name_value).replace(' ', '_')

csv_filename = f"{fighter_name_for_filename}_Fight_Data.csv"
combined_df.to_csv(csv_filename, index=False)
print(f"Data saved to '{csv_filename}'.")