INPUT_SCHEMA = {
    'name': {
        'type': str,
        'required': True
    },
    'lora_training_urls': {
        'type': str,
        'required': True
    },
    'mode': {
        'type': str,
        'required': False,
        'default': "object",
        'constraints': lambda width: width in ["face", "style", "object"]
    },
    'checkpoint': {
        'type': str,
        'required': False,
        'default': "sdxl-v1.0",
        'constraints': lambda width: width in ["sdxl-v1.0"]
    },
    'seed': {
        'type': int,
        'required': False,
        'default': -1,
    },
    'resolution': {
        'type': int,
        'required': False,
        'default': 1024,
        'constraints': lambda width: width % 16 == 0
    },
    'train_batch_size': {
        'type': int,
        'required': False,
        'default': 2,
    },
    'num_train_epochs': {
        'type': int,
        'required': False,
        'default': 10,
    },
    'max_train_steps': {
        'type': int,
        'required': False,
        'default': 5000,
    },
    'checkpointing_steps': {
        'type': int,
        'required': False,
        'default': 50000,
    },
    'is_lora': {
        'type': bool,
        'required': False,
        'default': True
    },
    'ti_lr': {
        'type': float,
        'required': False,
        'default': 1e-3
    },
    'ti_weight_decay': {
        'type': float,
        'required': False,
        'default': 1e-4
    },
    'lora_rank': {
        'type': int,
        'required': False,
        'default': 5
    },
    'lr_scheduler': {
        'type': str,
        'required': False,
        'default': "constant",
        'constraints': lambda width: width in ["constant", "linear"]
    },
    'lr_warmup_steps': {
        'type': int,
        'required': False,
        'default': 50
    },    
    'caption_prefix': {
        'type': str,
        'required': False,
        'default': "",
    },
    'left_right_flip_augmentation': {
        'type': bool,
        'required': False,
        'default': True
    },
    'mask_target_prompts': {
        'type': str,
        'required': False,
        'default': "",
    },
    'crop_based_on_salience': {
        'type': bool,
        'required': False,
        'default': True
    },
    'use_face_detection_instead': {
        'type': bool,
        'required': False,
        'default': False
    },
    'clipseg_temperature': {
        'type': float,
        'required': False,
        'default': 1.0
    },    
    'verbose': {
        'type': bool,
        'required': False,
        'default': True
    },
    'run_name': {
        'type': str,
        'required': False,
        'default': "",
    },
    'debug': {
        'type': bool,
        'required': False,
        'default': False
    },
    'hard_pivot': {
        'type': bool,
        'required': False,
        'default': True
    },
    'off_ratio_power': {
        'type': float,
        'required': False,
        'default': 0.1
    }
}