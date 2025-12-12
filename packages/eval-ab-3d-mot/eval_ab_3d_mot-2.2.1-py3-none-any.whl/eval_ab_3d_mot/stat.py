"""."""

from typing import Dict, Union


NUM_SAMPLE_POINTS = 41.0


class Stat:
    """
    Utility class to load data.
    """

    def __init__(self, t_sha: str, cls: str) -> None:
        """
        Constructor, initializes the object given the parameters.
        """

        # init object data
        self.mota = 0
        self.motp = 0
        self.F1 = 0
        self.precision = 0
        self.fp = 0
        self.fn = 0
        self.sMOTA = 0

        self.mota_list = list()
        self.motp_list = list()
        self.sMOTA_list = list()
        self.f1_list = list()
        self.precision_list = list()
        self.fp_list = list()
        self.fn_list = list()
        self.recall_list = list()

        self.t_sha = t_sha
        self.cls = cls

        self.sAMOTA = 0.0
        self.amota = 0.0
        self.amotp = 0.0

    def update(self, data: Dict[str, Union[float, int]]) -> None:
        self.mota += data['mota']
        self.motp += data['motp']
        self.F1 += data['F1']
        self.precision += data['precision']
        self.fp += data['fp']
        self.fn += data['fn']
        self.sMOTA += data['sMOTA']

        self.mota_list.append(data['mota'])
        self.motp_list.append(data['motp'])
        self.f1_list.append(data['F1'])
        self.precision_list.append(data['precision'])
        self.fp_list.append(data['fp'])
        self.fn_list.append(data['fn'])
        self.sMOTA_list.append(data['sMOTA'])

        self.recall_list.append(data['recall'])

    def output(self) -> None:
        self.sAMOTA = self.sMOTA / (NUM_SAMPLE_POINTS - 1)
        self.amota = self.mota / (NUM_SAMPLE_POINTS - 1)
        self.amotp = self.motp / (NUM_SAMPLE_POINTS - 1)

    def get_summary(self) -> str:
        summary = ''
        summary += 'evaluation: average over recall'.center(80, '=') + '\n'
        summary += ' sAMOTA  AMOTA  AMOTP \n'

        summary += '{:.4f} {:.4f} {:.4f}\n'.format(self.sAMOTA, self.amota, self.amotp)
        summary += '=' * 80
        return summary
