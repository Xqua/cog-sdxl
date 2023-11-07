''' infer.py for runpod worker '''

import json
import os
from pathlib import Path
from random import random
import shutil
import tarfile

import runpod
from runpod.serverless.utils import rp_download, rp_upload, rp_cleanup
from runpod.serverless.utils.rp_validator import validate
from bucket_connector import BucketConnector

from constants import SDXL_MODEL_CACHE

from preprocess import preprocess
from trainer_pti import main

from rp_schema import INPUT_SCHEMA

BUCKET = BucketConnector()

def run(job):
    '''
    Run inference on the model.
    Returns output path, width the seed used to generate the image.
    '''
    job_input = job['input']

    # Input validation
    validated_input = validate(job_input, INPUT_SCHEMA)

    if 'errors' in validated_input:
        return {"error": validated_input['errors']}
    validated_input = validated_input['validated_input']

    out_root_dir = "lora_models"

    if validated_input["checkpoint"] != "sdxl-v1.0":
        raise ValueError("Only sdxl-v1.0 is supported for now")

    if validated_input["mode"] == "face":
        validated_input["mask_target_prompts"] = "face"
    if validated_input["mode"] == "object":
        validated_input["mode"] = "concept"

    if validated_input["seed"] < 0:
        validated_input["seed"] = int(random()*100000)

    print("predict train_lora")
    print(validated_input)

    # Hard-code token_map for now. Make it configurable once we support multiple concepts or user-uploaded caption csv.
    token_string = "TOK"
    token_map = token_string + ":2"

    # Process 'token_to_train' and 'input_data_tar_or_zip'
    inserting_list_tokens = token_map.split(",")

    token_dict = {}
    running_tok_cnt = 0
    all_token_lists = []
    for token in inserting_list_tokens:
        n_tok = int(token.split(":")[1])
        token_dict[token.split(":")[0]] = "".join(
            [f"<s{i + running_tok_cnt}>" for i in range(n_tok)]
        )
        all_token_lists.extend([f"<s{i + running_tok_cnt}>" for i in range(n_tok)])
        running_tok_cnt += n_tok

    output_dir = os.path.join(out_root_dir, validated_input["run_name"])
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    input_dir, n_imgs, trigger_text, segmentation_prompt, captions = preprocess(
        output_dir,
        validated_input["mode"],
        input_zip_path = validated_input["lora_training_urls"],
        caption_text = validated_input["caption_prefix"],
        mask_target_prompts = validated_input["mask_target_prompts"],
        target_size = validated_input["resolution"],
        crop_based_on_salience = validated_input["crop_based_on_salience"],
        use_face_detection_instead = validated_input["use_face_detection_instead"],
        temp = validated_input["clipseg_temperature"],
        substitution_tokens = list(token_dict.keys()),
        left_right_flip_augmentation = validated_input["left_right_flip_augmentation"]
    )

    # Make a dict of all the arguments and save it to args.json: 

    validated_input["input_images"] = str(validated_input["lora_training_urls"])
    validated_input["num_training_images"] = n_imgs
    validated_input["token_string"] = token_string
    validated_input["trigger_text"] = trigger_text
    validated_input["segmentation_prompt"] = segmentation_prompt
    validated_input["trainig_captions"] = captions,


    with open(os.path.join(output_dir, "training_args.json"), "w") as f:
        json.dump(validated_input, f, indent=4)

    output_save_dir = main(
        pretrained_model_name_or_path = SDXL_MODEL_CACHE,
        instance_data_dir = os.path.join(input_dir, "captions.csv"),
        output_dir = output_dir,
        seed = validated_input["seed"],
        resolution = validated_input["resolution"],
        train_batch_size = validated_input["train_batch_size"],
        num_train_epochs = validated_input["num_train_epochs"],
        max_train_steps = validated_input["max_train_steps"],
        gradient_accumulation_steps = 1,
        ti_lr = validated_input["ti_lr"],
        ti_weight_decay = validated_input["ti_weight_decay"],
        lr_scheduler = validated_input["lr_scheduler"],
        lr_warmup_steps = validated_input["lr_warmup_steps"],
        token_dict = token_dict,
        inserting_list_tokens = all_token_lists,
        verbose = validated_input["verbose"],
        checkpointing_steps = validated_input["checkpointing_steps"],
        scale_lr = False,
        max_grad_norm = 1.0,
        allow_tf32 = True,
        mixed_precision = "bf16",
        device = "cuda:0",
        lora_rank = validated_input["lora_rank"],
        is_lora = validated_input["is_lora"],
        args_dict = validated_input["args_dict"],
        debug = validated_input["debug"],
        hard_pivot = validated_input["hard_pivot"],
        off_ratio_power = validated_input["off_ratio_power"],
    )

    validation_grid_img_path = os.path.join(output_save_dir, "validation_grid.jpg")
    out_path = "trained_model.tar"
    directory = Path(output_save_dir)

    with tarfile.open(out_path, "w") as tar:
        print("Adding files to tar...")
        for file_path in directory.rglob("*"):
            print(file_path)
            arcname = file_path.relative_to(directory)
            tar.add(file_path, arcname=arcname)

    lora_url = BUCKET.upload_tar(out_path, f"/loras/{validated_input['name']/out_path}")
    grid_url = BUCKET.upload_tar(validation_grid_img_path, f"/loras/{validated_input['name']}/validation_grid.jpg")

    print("LORA training finished!")
    print(f"Returning {out_path}")

    job_output = {
        "files": [lora_url], 
        "name": validated_input["name"], 
        "thumbnails": [grid_url], 
        "attributes": validated_input, 
        "isFinal": True, 
        "progress": 1.0
    }

    return job_output

runpod.serverless.start({"handler": run})