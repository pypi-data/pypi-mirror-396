def judge_same(*args, **kwargs):
    from kevin_toolbox.patches.for_test import check_consistency

    try:
        check_consistency(*args, **kwargs)
        return True
    except:
        return False


def determine_whether_to_add_trial(study, hyper_paras):
    from optuna.trial import TrialState

    for trial in study.trials:
        if judge_same(trial.params, hyper_paras) or judge_same(trial.system_attrs["fixed_params"], hyper_paras):
            if trial.state in [TrialState.COMPLETE, TrialState.RUNNING, TrialState.WAITING]:
                return False
            else:
                return True
    return True


def enqueue_trials_without_duplicates(study, hyper_paras_ls):
    res_ls = []  # 成功添加了的 trial
    for i, hyper_paras in enumerate(hyper_paras_ls):
        # 判断使用了该超参数的trial是否已经存在，如果不存在则添加
        if determine_whether_to_add_trial(study=study, hyper_paras=hyper_paras):
            study.enqueue_trial(params=hyper_paras)
            res_ls.append(i)
    return res_ls
