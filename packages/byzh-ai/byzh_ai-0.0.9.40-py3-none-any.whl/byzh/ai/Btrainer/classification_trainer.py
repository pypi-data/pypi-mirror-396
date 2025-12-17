import time
import torch

from .trainer import B_Trainer

class B_Classification_Trainer(B_Trainer):

    def calculate_model(self, dataloader=None, model=None, single_gpu=False):
        '''
        如果不指定, 则用类内的
        :param dataloader: 默认self.val_loader
        :param model: 默认self.model
        :return: accuracy, f1_score, confusion_matrix, inference_time, params
        '''
        if single_gpu:
            self._set_single_gpu()

        if dataloader==None:
            dataloader = self.val_loader
        if model==None:
            model = self.model
        model.eval()

        correct = 0
        total = 0
        y_true = []
        y_pred = []
        inference_time = []
        with torch.no_grad():
            for inputs, labels in dataloader:
                start_time = time.time()
                forward_out, labels, *args = self._forward(inputs, labels)
                end_time = time.time()

                predicted, sample_total, sample_correct = self.total_and_correct_func(forward_out, labels)

                self._spikingjelly_process()

                total += sample_total
                correct += sample_correct

                y_true.extend(labels.cpu().numpy())
                y_pred.extend(predicted.cpu().numpy())
                inference_time.append(end_time - start_time)

        # 平均推理时间
        inference_time = sum(inference_time) / len(inference_time)
        # acc & f1 & cm
        accuracy = correct / total
        f1_score = self.get_f1_score(y_true, y_pred)
        confusion_matrix = self.get_confusion_matrix(y_true, y_pred)
        # 参数量
        params = sum(p.numel() for p in model.parameters())

        info = f'[calc] accuracy: {accuracy:.3f}, f1_score: {f1_score:.3f}'
        self._print_and_toWriter(info)
        info = f'------ inference_time: {inference_time:.2e}s, params: {params / 1e3}K'
        self._print_and_toWriter(info)

        info = f'------ confusion_matrix:'
        self.writer.toFile(info)
        for content in str(confusion_matrix).split('\n'):
            info = f'------ \t{content}'
            self.writer.toFile(info)

        return accuracy, f1_score, confusion_matrix, inference_time, params


