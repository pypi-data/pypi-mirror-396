import torch
import torch.nn as nn
from .utils import get_pad_mask, get_subsequent_mask
from .layers import Encoder, Decoder


class B_Transformer(nn.Module):
    ''' A sequence to sequence model with attention mechanism. '''

    def __init__(
            self,
            n_src_vocab, n_tgt_vocab, # 词表大小
            src_pad_idx, tgt_pad_idx, # pad索引(如果某个词的数字是pad_idx, 则embedding为全0)
            d_word_vec=512, # 词嵌入维度
            d_model=512, # 模型的隐藏层维度
            d_ffn_hid=2048, # FFN层的隐藏层维度
            n_layers=6, # encoder/decoder的个数
            n_head=8, # 多头的头数
            d_k=64, d_v=64, # Query 和 Key 的维度相同
            dropout=0.1,
            n_position=200, # 位置编码支持的最大序列长度
            tgt_emb_prj_weight_sharing=True, # tgt的embedding 与 tgt的projection 权重共享
            emb_src_tgt_weight_sharing=True, # embedding权重共享(src, tgt)
            scale_emb_or_prj='prj' # embedding或projection的缩放控制
    ):
        '''
        d_q = d_k = d_v = d_word_vec / n_head
        '''
        super().__init__()

        self.src_pad_idx, self.tgt_pad_idx = src_pad_idx, tgt_pad_idx
        self.d_model = d_model

        assert d_model == d_word_vec, \
            'To facilitate the residual connections, \
             the dimensions of all module outputs shall be the same.'

        assert scale_emb_or_prj in ['emb', 'prj', 'none']
        scale_emb = (scale_emb_or_prj == 'emb') if tgt_emb_prj_weight_sharing else False
        self.scale_prj = (scale_emb_or_prj == 'prj') if tgt_emb_prj_weight_sharing else False
        # In section 3.4 of paper "Attention Is All You Need", there is such detail:
        # "In our model, we share the same weight matrix between the two
        # embedding layers and the pre-softmax linear transformation...
        # In the embedding layers, we multiply those weights by \sqrt{d_model}".
        #
        # Options here:
        #   'emb': multiply \sqrt{d_model} to embedding output
        #   'prj': multiply (\sqrt{d_model} ^ -1) to linear projection output
        #   'none': no multiplication

        # 除了n_tgt_vocab 都传入了
        self.encoder = Encoder(
            n_src_vocab=n_src_vocab, n_position=n_position,
            d_word_vec=d_word_vec, d_model=d_model, d_ffn_hid=d_ffn_hid,
            n_layers=n_layers, n_head=n_head, d_k=d_k, d_v=d_v,
            pad_idx=src_pad_idx, dropout=dropout, scale_emb=scale_emb)

        # 除了n_src_vocab, 都传入了
        self.decoder = Decoder(
            n_tgt_vocab=n_tgt_vocab, n_position=n_position,
            d_word_vec=d_word_vec, d_model=d_model, d_ffn_hid=d_ffn_hid,
            n_layers=n_layers, n_head=n_head, d_k=d_k, d_v=d_v,
            pad_idx=tgt_pad_idx, dropout=dropout, scale_emb=scale_emb)

        # 将 self.decoder 的输出 变换成 logits (不做softmax是因为CrossEntropy自带)
        self.tgt_word_prj = nn.Linear(d_model, n_tgt_vocab, bias=False)

        # 初始化权重(Xavier均匀分布)
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)

        # 权重共享
        if tgt_emb_prj_weight_sharing:
            self.tgt_word_prj.weight = self.decoder.tgt_word_emb.weight

        # 权重共享
        if emb_src_tgt_weight_sharing:
            self.encoder.src_word_emb.weight = self.decoder.tgt_word_emb.weight


    def forward(self, src_seq, tgt_seq):
        '''
        src_seq: [B, L_src]
        tgt_seq: [B, L_tgt]
        B是样本数(句子数), L是样本长度(句中单词数)
        '''
        # 生成mask矩阵(&是`按位与`)
        src_mask = get_pad_mask(src_seq, self.src_pad_idx) # [B, 1, L_src]
        tgt_mask = get_pad_mask(tgt_seq, self.tgt_pad_idx) & get_subsequent_mask(tgt_seq)  # [B, L_tgt, L_tgt]

        enc_output, *_ = self.encoder(src_seq, src_mask) # [B, L_src, d_word_vec]
        dec_output, *_ = self.decoder(tgt_seq, tgt_mask, enc_output, src_mask) # todo 看到这里
        seq_logit = self.tgt_word_prj(dec_output)

        if self.scale_prj:
            seq_logit *= self.d_model ** -0.5

        return seq_logit

if __name__ == '__main__':
    # ===== 超参数设置（与论文一致） =====
    batch_size = 2
    n_src_vocab = 1000 # 源语言词表大小
    n_tgt_vocab = 1000 # 目标语言词表大小
    src_pad_idx = 0 # 源语言padding的索引
    tgt_pad_idx = 0 # 目标语言padding的索引
    src_seq_len = 10 # 源语言序列长度
    tgt_seq_len = 12 # 目标语言序列长度

    # ===== 初始化模型 =====
    model = B_Transformer(
        n_src_vocab=n_src_vocab,
        n_tgt_vocab=n_tgt_vocab,
        src_pad_idx=src_pad_idx,
        tgt_pad_idx=tgt_pad_idx,
        d_word_vec=512, # 词嵌入维度
        d_model=512, # 模型的隐藏层维度
        d_ffn_hid=2048, # FFN层的隐藏层维度
        n_layers=6, # encoder/decoder的个数
        n_head=8, # 多头的头数
        d_k=64, # key的维度
        d_v=64, # value的维度
        dropout=0.1, # dropout比率
        n_position=200, # 位置编码支持的最大序列长度
        tgt_emb_prj_weight_sharing=True, # tgt的embedding 与 tgt的projection 权重共享
        emb_src_tgt_weight_sharing=True, # embedding权重共享(src, tgt)
        scale_emb_or_prj='prj' # embedding或projection的缩放控制
    )

    # ===== 随机生成输入序列 =====
    # 注意：token ID 范围必须小于 vocab size
    src_seq = torch.randint(1, n_src_vocab, (batch_size, src_seq_len)) # [B, L_src]
    tgt_seq = torch.randint(1, n_tgt_vocab, (batch_size, tgt_seq_len)) # [B, L_tgt]

    # ===== 前向传播 =====
    output = model(src_seq, tgt_seq)

    # ===== 输出信息 =====
    print(f"✅ src_seq shape: {src_seq.shape}") # torch.Size([2, 10])
    print(f"✅ tgt_seq shape: {tgt_seq.shape}") # torch.Size([2, 12])
    print(f"✅ output shape: {output.shape}") # torch.Size([2, 12, 1000])
    print(f"说明：output = (batch_size, tgt_seq_len, n_tgt_vocab)")