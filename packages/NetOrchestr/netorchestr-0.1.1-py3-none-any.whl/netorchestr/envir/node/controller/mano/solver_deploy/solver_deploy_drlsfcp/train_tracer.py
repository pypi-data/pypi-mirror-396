
import os
import csv
import torch
import time

from netorchestr.envir.node.controller.mano.solver_deploy.solver_deploy_drlsfcp.train_env import TrainEnv, TrainSolution

class SolverPerf:
    """Trace the solver result
    """
    def __init__(self) -> None:
        self.SOLVER_TIME = None
        self.SOLVER_RESUALT = None
        self.SOLVER_RESUALT_NODE = None
        self.SOLVER_RESUALT_LINK = None
        self.SOLVER_REJECTION = None
        self.SOLVER_ACTIONS = None
        self.SOLVER_REWARD = None

        self.LEARN_LR = None
        self.LEARN_LOSS = None
        self.LEARN_ACTOR_LOSS = None
        self.LEARN_CRITIC_LOSS = None
        self.LEARN_ENTROPY_LOSS = None
        self.LEARN_LOGPROB = None
        self.LEARN_RETURN = None

class SolverTracer:
    def __init__(self, save_dir:str, save_id:str, solver_name:str) -> None:
        self.save_dir = save_dir
        self.solver_name = solver_name
        
        self.save_file = os.path.join(save_dir, f"{solver_name}_trace.csv")
        self.model_file = os.path.join(save_dir, f"{solver_name}_model.pt")

    def handle_data(self,train_env: TrainEnv = None,learning_info: dict = None):
        data_save = SolverPerf()

        if train_env != None:
            data_save.SOLVER_TIME = train_env.time
            data_save.SOLVER_RESUALT = train_env.train_solution.result
            data_save.SOLVER_RESUALT_NODE = train_env.train_solution.place_result
            data_save.SOLVER_RESUALT_LINK = train_env.train_solution.route_result
            data_save.SOLVER_REJECTION = train_env.train_solution.rejection
            data_save.SOLVER_ACTIONS = train_env.train_solution.selected_actions
            data_save.SOLVER_REWARD = train_env.train_solution.reward
        
        if learning_info != None:
            data_save.LEARN_LR = learning_info.get('lr',None)
            data_save.LEARN_LOSS = learning_info.get('loss/loss',None)
            data_save.LEARN_ACTOR_LOSS = learning_info.get('loss/actor_loss',None)
            data_save.LEARN_CRITIC_LOSS = learning_info.get('loss/critic_loss',None)
            data_save.LEARN_ENTROPY_LOSS = learning_info.get('loss/entropy_loss',None)
            data_save.LEARN_LOGPROB = learning_info.get('value/logprob',None)
            data_save.LEARN_RETURN = learning_info.get('value/return',None)

        self.__save_record(data_save)
    
    def save_model(self,**kwargs):
        torch.save({
            'policy': kwargs['policy'], # self.policy.state_dict(),
            'optimizer': kwargs['optimizer'] # self.optimizer.state_dict(),
        }, self.model_file)

    def load_model(self, param_file_path):
        checkpoint = torch.load(param_file_path, weights_only=True)
        return checkpoint['policy'], checkpoint['optimizer']

    def __save_record(self,save_data:SolverPerf):
        head = None if os.path.exists(self.save_file) else list(save_data.__dict__.keys())
        with open(self.save_file, 'a+', newline='') as csv_file:
            writer = csv.writer(csv_file, dialect='excel', delimiter=',')
            if head is not None: writer.writerow(head)
            writer.writerow(list(save_data.__dict__.values()))
