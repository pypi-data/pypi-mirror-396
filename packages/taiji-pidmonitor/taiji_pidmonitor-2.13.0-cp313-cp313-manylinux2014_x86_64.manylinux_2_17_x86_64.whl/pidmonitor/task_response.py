import numpy as np
import time

def task_return_ini(array_length = 5):
    '''
    任务返回模板
    注：
        以'__'开头的键表示内部使用，main函数返回时自动过滤
    '''
    # 定义任务返回模板
    tasks_return_all = {
     'SP': np.zeros(array_length, dtype=float),  
     'OP': np.zeros(array_length, dtype=float),  
     'PV': np.zeros(array_length, dtype=float),  
     'MODE': np.zeros(array_length, dtype=float), 
     '__WPV': np.zeros(array_length, dtype=float), # WPV不用于客户端的显示
     'disp_x_axis': np.arange(0, array_length),  # 显示数据的横坐标
     # 'PV_const_score': 0, 
     # 'PV_const_array': np.zeros(array_length), 
     'device_load_score': -1, # 装置负荷得分
     'device_load_array': -1*np.ones(array_length, dtype=int),  # 装置负荷得分数组
     'MODE_EST': np.zeros(array_length, dtype=int),      # 估计出的MODE, 1905改名, 原名称为MODE_CALC
     'mode_est_auto_rate': 0, # 自控投运率, 1905改名, 原名称为mode_calc_auto_rate
     'mode_est_auto_totaltime': 0, # 自控时间长度，单位秒, 1905改名, 原名称为mode_calc_auto_totaltime
     'mode_est_manual_totaltime': 0, # 手动时间长度，单位秒, 1905改名, 原名称为mode_calc_manual_totaltime
     'auto_est_score_array': np.zeros(array_length, dtype=int), # 自动得分数组，1905新增，建议添加到画图
     'OP_saturation_score': 0,        # 阀门饱和得分
     'OP_saturation_array': np.zeros(array_length, dtype=int), #阀门饱和得分数组
     'OP_max': 0,    # OP最大值
     'OP_min': 0,    # OP最小值
     'OP_mean': 0,   # OP均值，新
     'OP_saturation_len': 0,   # 阀门饱和时长
     'OP_movement_count': 0,   # OP动作次数
     # 'saturation_value_array': np.array([],dtype=float),  # 阀门饱和位置数组
     'Loop_operating_state': 0,    # 回路运行状态
     'loop_state_str': '无效',    # 回路运行状态2, 2022-10-31新增
     'loop_state_str_EN': 'Invalid',    # 回路运行状态(英文), 2024-7新增
     'Loop_state_array': np.zeros(array_length,dtype=int), 
     'PV_bias_score': 0,    # PV偏差得分
     'PV_bias_array': np.zeros(array_length, dtype=int),  # PV偏差得分数组
     'PV_mean': 0,  # PV均值
     'SP_mean': 0,  # SP均值
     'PV_max': 0,  # PV最大
     'PV_min': 0,  # PV最小
     'PV_oscillation_score': 0,  # PV振荡得分
     'PV_oscillation_score_array': np.zeros(array_length, dtype=int), # PV振荡得分数组
     # 'PV_T_hat_array': np.zeros(array_length, dtype=int), # PV振荡周期数组，1905新增
     'OP_oscillation_score': 0,  # OP振荡得分
     'OP_oscillation_score_array': np.zeros(array_length, dtype=int), # OP振荡得分数组
     # 'OP_T_hat_array': np.zeros(array_length, dtype=int), # OP振荡周期数组，1905新增
     'SP_oscillation_score': 0,  # SP振荡得分
     'SP_oscillation_score_array': np.zeros(array_length, dtype=int), # SP振荡得分数组
     # 'SP_T_hat_array': np.zeros(array_length, dtype=int), # SP振荡周期数组，1905新增
     'LOOP_oscillation_score': 0,   # 回路振荡得分
     'LOOP_oscillation_score_array': np.zeros(array_length, dtype=int), # 回路振荡得分数组
     'Three_Sigma_num': 0, # 3-sigma配置文件，回路打分基准(benchmark)
     'PV_benchmark_score': 0, # PV控制性能得分
     'PV_benchmark_array': np.zeros(array_length, dtype=int), # PV控制性能得分基准
     'error_max': 0, # PV与SP最大正偏差（以后要改名）
     'error_min': 0, # PV与SP最大负偏差（以后要改名）
     'three_std_est': 0,  # 当前PV的3-sigma
     'comprehensive_score': 0,  # 回路综合得分
     'comprehensive_score_array': np.zeros(array_length, dtype=int), #回路综合得分数组
     'msg_array': np.array([0],dtype=int),   # 消息列表   # 新版不再支持(2022-04)。       
     'Monitor_Res_Msg_CN': '', # 综合性能评估结果，中文字符串   
     'Monitor_Res_Msg_EN': '', # 综合性能评估结果，英文字符串   
     'Msg_Str_1': '',  # 备用字符串
     'Msg_Str_2': '',  # 备用字符串 
     
     'Loop_nonlinear_rate': -1, # 回路非线性检测，2023-12新增
     'PID_integral_index': -1, # 回路积分强度检测，2023-12新增

    # 以下属性仅在故障诊断中返回计算数据
    'Diagnosis_Msg_Str_1': '',
    'Diagnosis_Msg_Str_2': 'Beautiful is better than ugly.', 

    'Diagnosis_Scatter_OP': np.arange(0, array_length),
    'Diagnosis_Scatter_PV': np.arange(0, array_length),
    'Diagnosis_Scatter_PrdLine_OP': np.arange(0, array_length),
    'Diagnosis_Scatter_PrdLine_PV': np.arange(0, array_length),

    'Diagnosis_freqs': np.linspace(0, 0.5, array_length),
    'Diagnosis_PVfft': np.ones(array_length),
    'Diagnosis_OPfft': np.ones(array_length),

    'Diagnosis_Valve_Stiction_x': np.arange(0, array_length),
    'Diagnosis_Valve_Stiction_y': np.arange(0, array_length),

    }
    return tasks_return_all

def task_state_ini():
    tasks_state_all = {'error_code_all':0, 
                       'warning_code_all':0, 
                       'work_flow_ctrl':0,
                       'data_sampling_time': 1,
                       'disp_sampling_time': 1,
                       'data_length': 5}
    return tasks_state_all


def join_result(loop_info, tasks_return_all, tasks_update_all, tasks_state_all):
    for key, value in tasks_return_all.items():
        if isinstance(value, np.ndarray):
            tasks_return_all[key] = value.tolist()
    for key, value in tasks_update_all.items():
        if isinstance(value, np.ndarray):
            tasks_update_all[key] = value.tolist()
    for key, value in tasks_state_all.items():
        if isinstance(value, np.ndarray):
            tasks_state_all[key] = value.tolist()
    loop_info['error_code'] = tasks_state_all['error_code_all']
    loop_info['warning'] = tasks_state_all['warning_code_all']
    loop_info['loop_remark_2'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    loop_dict_res_all = {'loop_info':loop_info, 
                        'loop_result':tasks_return_all,
                        'loop_setting_update':tasks_update_all}
    return loop_dict_res_all

def task_return_normal(loop_info, tasks_return_all, tasks_update_all, tasks_state_all):
    # 任务正常返回（包括出现错误代码的任务返回）
    # 数据慢采样
    web_task_return = {key: value for key, value in tasks_return_all.items() if not key.startswith('__')}
    for key, value in web_task_return.items():
        if isinstance(value, np.ndarray) or isinstance(value, list):
            if len(value) == tasks_state_all['data_length']:
                web_task_return[key] = web_task_return[key][::tasks_state_all['disp_sampling_time']]
    return join_result(loop_info, web_task_return, tasks_update_all, tasks_state_all)

def task_fail(Err_code, Err_Str): 
    # 出现致命错误时，返回基本模板
    tasks_return_all0 = task_return_ini()
    tasks_return_all = {key: value for key, value in tasks_return_all0.items() if not key.startswith('__')}
    tasks_update_all = {}
    tasks_state_all = task_state_ini()
    tasks_state_all['error_code_all'] = Err_code
    tasks_return_all['Monitor_Res_Msg_CN'] = "错误返回。"
    loop_info = {'loop_name': 'Monitor_Error',   # 回路名称，字符串，以原值返回
                'loop_id': 9999,       # 回路id，整数，以原值返回
                'save_csv': 0,           # 是否将loop_data的数据导出成csv文件
                'loop_remark_1': '1234', # 回路备注，字符串格式
                'loop_remark_2': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), # 回路备注，返回时修改为返回时间字符串
                'loop_remark_3': Err_Str, # 回路备注，字符串格式
                'loop_remark_4': '2345', # 回路备注，字符串格式
                'data_sampling_time': 1,  # 数据采样时间，整数，单位为秒，以原值返回
                'disp_sampling_time': 1,  # 数据显示时间，整数，单位为秒，返回的数据按要求慢采样，以原值返回
                'calculation_type':'pid_monitor',  # 填写计算类型，目前的可选值为: 'pid_monitor'(默认),'pid_sysid_tuning'
                'sysid_info': {},  # 如果指定的计算类型为'pid_sysid'，需加入此项，变量类型为字典，以原值返回。
                } 
    return join_result(loop_info, tasks_return_all, tasks_update_all, tasks_state_all)