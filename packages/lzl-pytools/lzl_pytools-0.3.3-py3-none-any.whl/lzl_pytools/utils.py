import csv
from datetime import datetime
import json
import logging
import time
import traceback
import sys

logger = logging.getLogger()

def time_str_to_int64(date_str, format_str="%Y-%m-%d %H:%M:%S"):
    time_obj = datetime.strptime(date_str, format_str)
    ts_second = time_obj.timestamp()
    ts_millisecond = int(ts_second * 1000)
    return ts_millisecond

def int64_millisecond_to_time_str(t, format_str="%Y-%m-%d %H:%M:%S"):
    t = t/1000.0
    t = time.localtime(t)
    return time.strftime(format_str, t)

def retry_run(func, times=10, fail_sleep_time=1, err_logger=None):
    for i in range(times):
        try:
            return func()
        except:
            if err_logger:
                err_logger.error(f"retry_run error: {i}/{times}, sleep={fail_sleep_time}. {traceback.format_exc()}")
            time.sleep(fail_sleep_time)
    return func()

def save_json(path, obj, encoding='utf-8', indent=2):
    with open(path, 'w', encoding=encoding) as f:
        json.dump(obj, f, indent=indent, ensure_ascii=False)

def load_json(path, encoding='utf-8'):
    with open(path, encoding=encoding) as f:
        obj = json.load(f)
        return obj

def csv_write(filepath, datas, header=None, encoding='utf-8'):
    with open(filepath, 'w', newline='', encoding=encoding) as f:
        writer = csv.writer(f)
        if header:
            writer.writerow(header)
        writer.writerows(datas)

def csv_read(filepath, encoding='utf-8'):
    with open(filepath, 'r', encoding=encoding) as f:
        reader = csv.reader(f)
        datas = list(reader)
        return datas

def read_file_lines(path, skip_null_line=False, encoding='utf-8'):
    def _skip_null_line(lines):
        outs =[]
        for line in lines:
            if line.strip() == '':
                continue
            outs.append(line)
        return outs
    lines = None
    with open(path, encoding=encoding) as f:
        lines = f.readlines()
    if skip_null_line:
        return _skip_null_line(lines)
    return lines

def read_file_lines_auto_encoding(path, skip_null_line=False):
    try:
        return read_file_lines(path, skip_null_line, 'utf-8')
    except:
        return read_file_lines(path, skip_null_line, 'GB18030')

def write_file_lines(path, lines, encoding='utf-8'):
    with open(path, 'w', encoding=encoding) as f:
        if type(lines) == type([]):
            for line in lines:
                f.writelines(line)
                f.writelines('\n')
        else:
            f.writelines(lines)

def list_to_dict(values, keys):
    return dict([keys[idx], val] for idx, val in enumerate(values))

# 将rowdatas的数据搞成对齐的格式，输出outDatas
def format_table(rowdatas, header=None, leftAlign=False, headerSep=True):
    datas = rowdatas[:]
    if header:
        if headerSep:
            datas.insert(0, ['']*len(header))
        datas.insert(0, header)
        if headerSep:
            datas.insert(0, ['']*len(header))
    rows = len(datas)
    cols = len(datas[0])
    colMaxLen = []
    for c in range(0, cols):
        maxlen = 2
        for r in range(0, rows):
            # 中文暂占两个，gbk刚刚满足条件
            bytelen = len(bytes(str(datas[r][c]), encoding='gbk'))
            if bytelen > maxlen:
                maxlen = bytelen
        colMaxLen.append(maxlen + 2)  # 留两个空格
    outDatas = []
    for r in range(0, rows):
        s = []
        for c in range(0, cols):
            bytelen = len(bytes(str(datas[r][c]), encoding='gbk'))
            if leftAlign:
                s.append('%s%s' % (str(datas[r][c]), ' ' * (colMaxLen[c] - bytelen)))
            else:
                s.append('%s%s' % (' ' * (colMaxLen[c] - bytelen), str(datas[r][c])))
        outDatas.append(s)
    if header and headerSep:
        for i in range(0, len(outDatas[0])):
            outDatas[2][i] = '-'*len(outDatas[0][i])
            outDatas[0][i] = '-'*len(outDatas[2][i])
    return outDatas

def table_to_format_str(rowdatas, header=None, sepStr=' | ', leftAlign=False, headerSep=False):
    outDatas = format_table(rowdatas, header, leftAlign, headerSep=headerSep)
    outs = []
    for row in outDatas:
        s = sepStr.join(row)
        outs.append(s)
    return outs

# 格式化打印二维表，每列对齐
def format_print_table(rowdatas, header=None, sepStr=' | ', leftAlign=False, outFile=sys.stdout):
    lines = table_to_format_str(rowdatas, header, sepStr, leftAlign)
    for line in lines:
        outFile.writelines(line)
        outFile.writelines('\n')

def split_range(start: int, end: int, n_groups: int):
    """ 将左闭右开区间 [start, end) 分成 n_groups 个左闭右开的子区间 [a, b) """
    group_size = (end - start) // n_groups
    remainder = (end - start) % n_groups
    if group_size <= 0:
        return [[i, i+1] for i in range(start, end)]
    groups = []
    current_start = start
    for i in range(n_groups):
        current_group_size = group_size + (1 if i < remainder else 0)
        current_end = current_start + current_group_size
        groups.append([current_start, current_end])
        current_start = current_end
    return groups

def build_tasks(start, end, query_cnt_func, finish_min_count=16000):
    query_stack = []
    query_stack.append([start, end])
    while len(query_stack) > 0:
        query_start, query_end = query_stack.pop()
        cnt = query_cnt_func(query_start, query_end)
        group_size = query_end - query_start
        if cnt == 0:
            continue
        elif cnt <= finish_min_count:
            yield 'task', query_start, query_end, group_size, cnt
            continue
        if query_end - query_start <= 1:
            yield 'error', query_start, query_end, group_size, cnt
            continue
        if cnt < finish_min_count * 2:
            query_stack += split_range(query_start, query_end, 2)
        elif cnt < finish_min_count * 3:
            query_stack += split_range(query_start, query_end, 3)
        elif cnt < finish_min_count * 5:
            query_stack += split_range(query_start, query_end, 5)
        else:
            query_stack += split_range(query_start, query_end, 10)

def build_tasks_with_process(start, end, query_cnt_func, finish_min_count=16000, show_log_cnt = 1000):
    tasks = []
    err_tasks = []
    all_cnt = query_cnt_func(start, end)
    logger.warning(f"==> build tasks start: all_cnt={all_cnt}, start={start}, end={end}")
    if all_cnt == 0:
        logger.warning(f"==> build tasks stop: all_cnt = 0, nothing to do.")
        return tasks, err_tasks

    query_cnt, data_num = 0, 0
    def _query_count(start, end):
        nonlocal query_cnt
        query_cnt += 1
        if query_cnt % show_log_cnt == 0:
            logger.warning(f"==> build tasks: query_cnt={query_cnt}, task_num={len(tasks)}, err_task_num={len(err_tasks)}, cur_cnt={data_num}, progress={float(data_num)*100/all_cnt:.1f}%")
        return query_cnt_func(start, end)
    for t, query_start, query_end, group_size, cnt in build_tasks(start, end, _query_count, finish_min_count):
        data_num += cnt
        if t == 'task':
            tasks.append([query_start, query_end, group_size, cnt])
        else:
            err_tasks.append([query_start, query_end, group_size, cnt])
    logger.warning(f"==> build tasks stop: query_cnt={query_cnt}, task_num={len(tasks)}, err_task_num={len(err_tasks)}, cur_cnt={data_num}, all_cnt={all_cnt}")
    return tasks, err_tasks

# def test():
#     outs = [
#         [1, 2, 4, 6],
#         [1, 2, 4, 6],
#         [1, 2, 4, 6],
#         [1, 2, 4, 6],
#     ]
#     rows = table_to_format_str(outs)
#     write_file_lines('test.txt', rows)
#     print(read_file_lines_auto_encoding('test.txt', True))
#     csv_write('test.csv', outs)
#     print(csv_read('test.csv'))
#     save_json('test.json', outs)
#     print(load_json('test.json'))
#     print(time_str_to_int64('2025-1-1 10:11:11'))
#     print(int64_millisecond_to_time_str(1735726271000))
# test()