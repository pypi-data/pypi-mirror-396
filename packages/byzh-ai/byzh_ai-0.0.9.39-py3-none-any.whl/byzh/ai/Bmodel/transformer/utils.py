import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math

def get_pad_mask(seq, pad_idx):
    '''
    得到一个布尔矩阵(False表示pad位置)
    seq: [B, L]
    pad_idx: int
    return: [B, 1, L]
    '''
    return (seq != pad_idx).unsqueeze(-2)


def get_subsequent_mask(seq):
    '''
    得到一个布尔矩阵(False表示不能看到的未来位置)
    seq: [B, L]
    return: [B, L, L]
    '''
    B, L = seq.size()
    # torch.triu(..., diagonal=1)使右上三角为1
    # 1-...使右上三角为0, 左下三角为1
    subsequent_mask = (1 - torch.triu(torch.ones((1, L, L)), diagonal=1))
    subsequent_mask = subsequent_mask.bool()
    subsequent_mask = subsequent_mask.to(seq.device)
    return subsequent_mask

class PositionalEncoding(nn.Module):

    def __init__(self, d_word_vec, n_position=200):
        '''
        d_word_vec: 词向量的维度
        n_position: 位置编码的长度
        '''
        super().__init__()

        # 注册一个张量 pos_table，但它不是参数（不会被优化器更新）
        # 会随着模型保存/加载，但不会参与梯度计算
        self.register_buffer('pos_table', self._get_sinusoid_encoding_table(n_position, d_word_vec))

    # def _get_sinusoid_encoding_table(self, n_position, d_word_vec):
    #     ''' 生成正弦波位置编码表(numpy) '''
    #
    #     def get_position_angle_vec(position):
    #         return [position / np.power(10000, 2 * (hid_j // 2) / d_word_vec) for hid_j in range(d_word_vec)]
    #
    #     sinusoid_table = np.array([get_position_angle_vec(pos_i) for pos_i in range(n_position)])
    #     sinusoid_table[:, 0::2] = np.sin(sinusoid_table[:, 0::2])  # dim 2i
    #     sinusoid_table[:, 1::2] = np.cos(sinusoid_table[:, 1::2])  # dim 2i+1
    #
    #     return torch.FloatTensor(sinusoid_table).unsqueeze(0)

    def _get_sinusoid_encoding_table(self, n_position, d_word_vec):
        ''' 生成正弦位置编码表(pytorch) '''

        # 1. 生成 [n_position, 1] 的位置索引
        position = torch.arange(0, n_position, dtype=torch.float32).unsqueeze(1)
        # 2. 生成 [d_word_vec // 2] 的 div_term
        div_term = torch.exp(torch.arange(0, d_word_vec, 2).float() * -(math.log(10000.0) / d_word_vec))
        # 3. 构建 sin 和 cos
        sinusoid_table = torch.zeros(n_position, d_word_vec)
        sinusoid_table[:, 0::2] = torch.sin(position * div_term)  # 偶数维 sin
        sinusoid_table[:, 1::2] = torch.cos(position * div_term)  # 奇数维 cos
        # 4. 增加 batch 维度 [1, n_position, d_word_vec]
        return sinusoid_table.unsqueeze(0)

    def forward(self, x):
        '''
        x: [B, L, d_word_vec]
        '''
        _, L, _ = x.size()
        position =  self.pos_table[:, :L, :] # 位置信息
        position = position.clone().detach() # 位置信息不参与反向传播
        result = x + position
        return result


class ScaledDotProductAttention(nn.Module):
    ''' Scaled Dot-Product Attention '''

    def __init__(self, scale_factor, dropout=0.1):
        super().__init__()
        self.scale_factor = scale_factor
        self.dropout = nn.Dropout(dropout)

    def forward(self, q, k, v, mask=None):
        '''
        当L2=L_src时, any=1 (自动广播到L_src或L_tgt)
        当L2=L_tgt时, any=L_tgt (因为有mask编码)
        对于encoder的self-attention的mask: [B, n_head, 1, L_src]
            mask用于padding(防止encoder关注到<PAD>)
        对于encoder的self-attention的mask: [B, n_head, L_tgt, L_tgt]
            mask用于padding以及防止观看未来信息
        对于decoder的enc-dec-attention的mask: [B, n_head, 1, L_src]
            mask用于padding(防止decoder关注到encoder的<PAD>)

        q: [B, n_head, len_q=L1, d_k]
        k: [B, n_head, len_k=L2, d_k]
        v: [B, n_head, len_v=L2, d_v]
        mask: [B, n_head, any, L2]
        '''
        # QK相乘, 得到词与词之间的相关性矩阵(第i个query[当前词] 对 第j个key[候选词] 的相关性)
        attn = q @ k.transpose(2, 3) # [B, n_head, L1, L2]
        attn = attn / self.scale_factor
        if mask is not None:
            # 给mask的值一个-inf, softmax后约为0，不参与注意力计算
            # mask 决定了每个 query 能看到哪些 key
            attn = attn.masked_fill(mask == 0, -1e9)

        # 计算得到各个词之间的权重
        attn = F.softmax(attn, dim=-1)
        attn = self.dropout(attn) # [B, n_head, L1, L2]
        output = torch.matmul(attn, v) # [B, n_head, L1, d_v]

        return output, attn

class MultiHeadAttention(nn.Module):
    ''' Multi-Head Attention module '''

    def __init__(self, n_head, d_model, d_k, d_v, dropout=0.1):
        super().__init__()

        self.n_head = n_head
        self.d_k = d_k
        self.d_v = d_v

        self.w_qs = nn.Linear(d_model, n_head * d_k, bias=False) # W_Q: [n_head*d_k, n_head*d_k]
        self.w_ks = nn.Linear(d_model, n_head * d_k, bias=False) # W_K: [n_head*d_k, n_head*d_k]
        self.w_vs = nn.Linear(d_model, n_head * d_v, bias=False) # W_V: [n_head*d_v, n_head*d_v]
        self.fc = nn.Linear(n_head * d_v, d_model, bias=False) # W^O: [n_head*d_v, n_head*d_v]

        self.attention = ScaledDotProductAttention(scale_factor=d_k ** 0.5)

        self.dropout = nn.Dropout(dropout)


    def forward(self, q, k, v, mask=None):
        '''
        L1 = len_q
        L2 = len_k = len_v

        q: [B, L1, d_word_vec==d_model==n_head*d_k]
        k: [B, L2, d_word_vec==d_model==n_head*d_k]
        v: [B, L2, d_word_vec==d_model==n_head*d_v]
        mask: [B, any, L2]
        '''
        B, len_q, len_k, len_v = q.size(0), q.size(1), k.size(1), v.size(1)

        # 拆成多头: [B, L, head*d] -> [B, L, head, d]
        q = self.w_qs(q).view(B, len_q, self.n_head, self.d_k) # [B, len_q, n_head, d_k]
        k = self.w_ks(k).view(B, len_k, self.n_head, self.d_k) # [B, len_k, n_head, d_k]
        v = self.w_vs(v).view(B, len_v, self.n_head, self.d_v) # [B, len_v, n_head, d_v]

        # 形状调整: [B, L, head, d] -> [B, head, L, d]
        q, k, v = q.transpose(1, 2), k.transpose(1, 2), v.transpose(1, 2)
        # q: [B, n_head, len_q, d_k]
        # k: [B, n_head, len_k, d_k]
        # v: [B, n_head, len_v, d_v]

        if mask is not None:
            # 给mask添加n_head的广播
            mask = mask.unsqueeze(1) # [B, n_head, any, L2]

        q, attn = self.attention(q, k, v, mask=mask)
        # q: [B, n_head, L1, d_v]
        # attn: [B, n_head, L1, L2]

        # 把多头拼回来: [B, head, L, d] -> [B, L, head, d] -> [B, L, head*d]
        q = q.transpose(1, 2).contiguous().view(B, len_q, -1)
        # q: [B, L1, d_word_vec==d_model==n_head*d_k]

        # dropout正则
        q = self.dropout(self.fc(q))

        return q, attn


class PositionwiseFeedForward(nn.Module):
    ''' A two-feed-forward-layer module '''

    def __init__(self, d_in, d_hid, dropout=0.1):
        super().__init__()
        self.w_1 = nn.Linear(d_in, d_hid) # position-wise
        self.relu = nn.ReLU()
        self.w_2 = nn.Linear(d_hid, d_in) # position-wise

        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        '''
        x: [B, L, d_word_vec]
        '''
        x = self.w_1(x)
        x = self.relu(x)
        x = self.w_2(x)

        # dropout正则
        x = self.dropout(x) # [B, L, d_word_vec]

        return x





