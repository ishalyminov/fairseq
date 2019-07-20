import argparse
import datetime
import os


def get_args():
    parser = argparse.ArgumentParser('Script for launching hyperparameter sweeps')
    parser.add_argument('-d', '--data', help='path to data directory')
    parser.add_argument('-p', '--prefix', required=True,
                        help='save checkpoints and logs in <checkpoints-dir>/<prefix>.<save_dir_key>')
    parser.add_argument('-t', '--num-trials', required=True, type=int,
                        help='number of random hyperparam configurations to try (-1 for grid search)')
    parser.add_argument('-g', '--num-gpus', type=int, required=True, help='number of GPUs per node')
    parser.add_argument('-n', '--num-nodes', type=int, default=1, help='number of nodes for distributed training')
    parser.add_argument('--seed', type=int, default=1234)
    parser.add_argument('--baseline-model', help='path to baseline model from which to resume training')
    parser.add_argument('--checkpoints-dir',
                        default=os.path.join(
                            '/mnt/vol/gfsai-east/ai-group/users',
                            os.environ['USER'],
                            'checkpoints',
                            str(datetime.date.today()),
                        ),
                        help='save checkpoints and logs in <checkpoints-dir>/<prefix>.<save_dir_key>')
    parser.add_argument('--force-checkpoints-dir', help='force using a given checkpoint dir')
    parser.add_argument('--dry-run', action='store_true',
                        help='output only a list of actions to perform without performing them')
    parser.add_argument('--local', action='store_true', help='run job locally')
    parser.add_argument('--debug', action='store_true', help='debug')

    parser.add_argument('--backend', choices=['fblearner', 'chronos'], default='fblearner')

    # FBLearner params
    parser.add_argument('--entitlement', help='entitlement to use', default='gpu_fair')
    parser.add_argument('--run-as-secure-group', help='secure group to use', default='oncall_fairseq')

    # Chronos params
    parser.add_argument('--hostgroup', help='hostgroup to use')
    parser.add_argument('--host-filter', help='host filter')
    parser.add_argument('--fbpkg', help='use the given fbpkg')
    parser.add_argument('--build-only', action='store_true')

    args = parser.parse_args()
    return args


class hyperparam(object):
    """Base class for defining hyperparameters."""

    def __init__(self, name, values=None, binary_flag=False, save_dir_key=None):
        """
        Arguments:
        - name : the name of the hyperparameter (e.g., `--dropout`)
        - values : the set of values to sweep over (e.g., `[0.0, 0.1, 0.2]`)
        - binary_flag : whether the hyperparameter uses a boolean flag (e.g., `--no-save`)
        - save_dir_key : function that takes the hyperparameter value and returns the "key"
                         to be appended to the output directory name
        """
        self.name = name
        if values is None:  # syntactic sugar for binary flags
            self.values = [True]
            self.binary_flag = True
        else:
            self.values = values if isinstance(values, list) else [values]
            self.binary_flag = binary_flag
        self.save_dir_key = save_dir_key
        self.current_value = None

        if len(self.values) > 1 and self.save_dir_key is None:
            raise ValueError(f'{name} has more than one value but is missing a save_dir_key!')

    def get_cli_args(self):
        if self.binary_flag:
            return [self.name] if self.current_value else []
        else:
            return [self.name, self.current_value]

    def get_save_dir_key(self):
        if self.save_dir_key is None:
            return None
        if self.binary_flag:
            return self.save_dir_key(1) if self.current_value else None
        return self.save_dir_key(self.current_value)


def main(get_grid, postprocess_hyperparams):
    args = get_args()

    if args.backend == 'fblearner':
        from .fblearner import main as backend_main
    elif args.backend == 'chronos':
        from .chronos import main as backend_main

    backend_main(get_grid, postprocess_hyperparams, args)
