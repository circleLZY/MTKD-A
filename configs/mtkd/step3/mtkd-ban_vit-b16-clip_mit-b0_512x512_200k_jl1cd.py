_base_ = [
    '../../_base_/models/mtkd/mtkd-ban_vit-b16.py', 
    '../../common/standard_512x512_200k_jl1cd.py']

crop_size = (512, 512)

checkpoint_student = None
checkpoint_teacher_l = None
checkpoint_teacher_m = None
checkpoint_teacher_s = None

# model settings
model = dict(
    init_cfg=dict(type='Pretrained', checkpoint=checkpoint_student),
    # teacher large    
    init_cfg_t_l = dict(type='Pretrained', checkpoint=checkpoint_teacher_l),
    # teacher medium    
    init_cfg_t_m = dict(type='Pretrained', checkpoint=checkpoint_teacher_m),
    # teacher small    
    init_cfg_t_s = dict(type='Pretrained', checkpoint=checkpoint_teacher_s),
    
    asymetric_input=True,
    encoder_resolution=dict(
        size=(224, 224),
        mode='bilinear'),
    image_encoder=dict(
        frozen_exclude=[]),
    decode_head=dict(
        type='BitemporalAdapterHead',
        ban_cfg=dict(
            clip_channels=768,
            fusion_index=[1, 2, 3],
            side_enc_cfg=dict(
                type='mmseg.MixVisionTransformer',
                in_channels=3,
                embed_dims=32,
                num_stages=4,
                num_layers=[2, 2, 2, 2],
                num_heads=[1, 2, 5, 8],
                patch_sizes=[7, 3, 3, 3],
                sr_ratios=[8, 4, 2, 1],
                out_indices=(0, 1, 2, 3),
                mlp_ratio=4,
                qkv_bias=True,
                drop_rate=0.0,
                attn_drop_rate=0.0,
                drop_path_rate=0.1)),
        ban_dec_cfg=dict(
            type='BAN_MLPDecoder',
            in_channels=[32, 64, 160, 256],
            channels=128,
            dropout_ratio=0.1,
            num_classes=2,
            norm_cfg=dict(type='SyncBN', requires_grad=True),
            align_corners=False)),
    test_cfg=dict(mode='slide', crop_size=crop_size, stride=(crop_size[0]//2, crop_size[1]//2)))

optim_wrapper = dict(
    _delete_=True,
    type='AmpOptimWrapper',
    optimizer=dict(
        type='AdamW', lr=0.0001, betas=(0.9, 0.999), weight_decay=0.0001),
    paramwise_cfg=dict(
        custom_keys={
            'img_encoder': dict(lr_mult=0.1, decay_mult=1.0),
            'norm': dict(decay_mult=0.),
            'mask_decoder': dict(lr_mult=10.)
        }),
    loss_scale='dynamic',
    clip_grad=dict(max_norm=0.01, norm_type=2))

train_dataloader = dict(batch_size=8, num_workers=8)
val_dataloader = dict(batch_size=1, num_workers=1)