import torch.nn as nn
from .utils import PositionalEncoding, MultiHeadAttention, PositionwiseFeedForward

##### Encoder #####
class EncoderLayer(nn.Module):
    ''' Compose with two layers '''

    def __init__(self, d_model, d_ffn_hid, n_head, d_k, d_v, dropout=0.1):
        super().__init__()
        self.slf_attn = MultiHeadAttention(n_head, d_model, d_k, d_v, dropout=dropout)
        self.layer_norm_1 = nn.LayerNorm(d_model, eps=1e-6)

        self.pos_ffn = PositionwiseFeedForward(d_model, d_ffn_hid, dropout=dropout)
        self.layer_norm_2 = nn.LayerNorm(d_model, eps=1e-6)
    def forward(self, enc_input, slf_attn_mask=None):
        '''
        enc_input: [B, L_src, d_word_vec]
        slf_attn_mask: [B, 1, L_src]
        '''
        # Multi-Head Attention
        q, k, v = enc_input, enc_input, enc_input # 输入copy成三份作为Q, K, V
        residual = q
        enc_output, enc_slf_attn = self.slf_attn(
            q, k, v, mask=slf_attn_mask
        )
        # Add
        enc_output = enc_output + residual
        # Norm
        enc_output = self.layer_norm_1(enc_output)
        # -> enc_output: [B, L_src, d_word_vec]
        # -> enc_slf_attn: [B, n_head, L_src, L_src]

        # Feed Forward
        residual = enc_output
        enc_output = self.pos_ffn(enc_output)
        # Add
        enc_output = enc_output + residual
        # Norm
        enc_output = self.layer_norm_2(enc_output)
        # -> enc_output: [B, L_src, d_word_vec]

        return enc_output, enc_slf_attn
class Encoder(nn.Module):
    ''' A encoder model with self attention mechanism. '''

    def __init__(
            self, n_src_vocab, d_word_vec, n_layers, n_head, d_k, d_v,
            d_model, d_ffn_hid, pad_idx, dropout=0.1, n_position=200, scale_emb=False):
        super().__init__()

        # 词嵌入向量
        self.src_word_emb = nn.Embedding(n_src_vocab, d_word_vec, padding_idx=pad_idx)
        # 位置编码
        self.position_enc = PositionalEncoding(d_word_vec, n_position=n_position)
        # dropout正则
        self.dropout = nn.Dropout(p=dropout)
        # encoder堆栈
        self.layer_stack = nn.ModuleList([
            EncoderLayer(d_model, d_ffn_hid, n_head, d_k, d_v, dropout=dropout)
            for _ in range(n_layers)
        ])
        self.layer_norm = nn.LayerNorm(d_model, eps=1e-6)
        self.scale_emb = scale_emb
        self.d_model = d_model

    def forward(self, src_seq, src_mask, return_attns=False):
        '''
        src_seq: [B, L_src]
        src_mask: [B, 1, L_src]
        '''
        enc_slf_attn_list = []

        # 词嵌入向量
        enc_output = self.src_word_emb(src_seq) # [B, L_src, d_word_vec]
        if self.scale_emb:
            enc_output *= self.d_model ** 0.5
        # 位置编码
        enc_output = self.position_enc(enc_output)
        # dropout正则+layernorm
        enc_output = self.dropout(enc_output)
        enc_output = self.layer_norm(enc_output)
        # encoder堆栈
        for enc_layer in self.layer_stack:
            enc_output, enc_slf_attn = enc_layer(enc_output, slf_attn_mask=src_mask)
            # enc_output: [B, L_src, d_word_vec]
            # enc_slf_attn: [B, n_head, L_src, L_src]
            enc_slf_attn_list += [enc_slf_attn] if return_attns else []

        if return_attns:
            return enc_output, enc_slf_attn_list
        return enc_output,


##### Decoder #####
class DecoderLayer(nn.Module):
    ''' Compose with three layers '''

    def __init__(self, d_model, d_ffn_hid, n_head, d_k, d_v, dropout=0.1):
        super().__init__()
        self.slf_attn = MultiHeadAttention(n_head, d_model, d_k, d_v, dropout=dropout)
        self.layer_norm_1 = nn.LayerNorm(d_model, eps=1e-6)

        self.enc_attn = MultiHeadAttention(n_head, d_model, d_k, d_v, dropout=dropout)
        self.layer_norm_2 = nn.LayerNorm(d_model, eps=1e-6)

        self.pos_ffn = PositionwiseFeedForward(d_model, d_ffn_hid, dropout=dropout)
        self.layer_norm_3 = nn.LayerNorm(d_model, eps=1e-6)

    def forward(self, dec_input, enc_output, slf_attn_mask=None, dec_enc_attn_mask=None):
        '''
        L1=len_q
        L2=len_k=len_v

        dec_input: [B, L_tgt, d_word_vec]
        enc_output: [B, L_src, d_word_vec]
        slf_attn_mask: [B, L_tgt, L_tgt]
        dec_enc_attn_mask: [B, 1, L_src]
        '''
        # Masked Multi-Head Attention
        q, k, v = dec_input, dec_input, dec_input # 输入copy成三份作为Q, K, V
        residual = q
        dec_output, dec_slf_attn = self.slf_attn(q, k, v, mask=slf_attn_mask)
        # Add
        dec_output = dec_output + residual
        # Norm
        dec_output = self.layer_norm_1(dec_output)
        # -> dec_output: [B, L_tgt, d_word_vec]
        # -> dec_slf_attn: [B, n_head, L_tgt, L_tgt]

        # Multi-Head Attention
        q, k, v = dec_output, enc_output, enc_output # k, v来自encoder的输出
        residual = q
        dec_output, dec_enc_attn = self.enc_attn(q, k, v, mask=dec_enc_attn_mask)
        # Add
        dec_output = dec_output + residual
        # Norm
        dec_output = self.layer_norm_2(dec_output)
        # -> dec_output: [B, L_tgt, d_word_vec]
        # -> dec_enc_attn: [B, n_head, L_tgt, L_src]

        # Feed Forward
        residual = dec_output
        dec_output = self.pos_ffn(dec_output)
        # Add
        dec_output = dec_output + residual
        # Norm
        dec_output = self.layer_norm_3(dec_output)
        # -> [B, L_tgt, d_word_vec]

        return dec_output, dec_slf_attn, dec_enc_attn

class Decoder(nn.Module):
    ''' A decoder model with self attention mechanism. '''

    def __init__(
            self, n_tgt_vocab, d_word_vec, n_layers, n_head, d_k, d_v,
            d_model, d_ffn_hid, pad_idx, n_position=200, dropout=0.1, scale_emb=False):

        super().__init__()

        self.tgt_word_emb = nn.Embedding(n_tgt_vocab, d_word_vec, padding_idx=pad_idx)
        self.position_enc = PositionalEncoding(d_word_vec, n_position=n_position)
        self.dropout = nn.Dropout(p=dropout)
        self.layer_stack = nn.ModuleList([
            DecoderLayer(d_model, d_ffn_hid, n_head, d_k, d_v, dropout=dropout)
            for _ in range(n_layers)
        ])
        self.layer_norm = nn.LayerNorm(d_model, eps=1e-6)
        self.scale_emb = scale_emb
        self.d_model = d_model

    def forward(self, tgt_seq, tgt_mask, enc_output, src_mask, return_attns=False):
        '''
        tgt_seq: [B, L_tgt]
        tgt_mask: [B, L_tgt, L_tgt]
        enc_output: [B, L_src, d_word_vec]
        src_mask: [B, 1, L_src]
        '''
        dec_slf_attn_list, dec_enc_attn_list = [], []

        # 词嵌入向量
        dec_output = self.tgt_word_emb(tgt_seq)
        if self.scale_emb:
            dec_output *= self.d_model ** 0.5
        # 位置编码
        dec_output = self.position_enc(dec_output)
        # dropout正则+layernorm
        dec_output = self.dropout(dec_output)
        dec_output = self.layer_norm(dec_output) # [B, L_tgt, d_word_vec]

        # decoder堆栈
        for dec_layer in self.layer_stack:
            dec_output, dec_slf_attn, dec_enc_attn = dec_layer(
                dec_output, enc_output,
                slf_attn_mask=tgt_mask, dec_enc_attn_mask=src_mask
            )
            # dec_output: [B, L_tgt, d_word_vec]
            # dec_slf_attn: [B, n_head, L_tgt, L_tgt]
            # dec_enc_attn: [B, n_head, L_tgt, L_src]
            dec_slf_attn_list += [dec_slf_attn] if return_attns else []
            dec_enc_attn_list += [dec_enc_attn] if return_attns else []

        if return_attns:
            return dec_output, dec_slf_attn_list, dec_enc_attn_list
        return dec_output,