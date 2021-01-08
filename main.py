import torch
import sys
import time
import argparse

from torchvision import datasets, models, transforms
from transformers import AutoTokenizer, AutoModel

def sec_to_ms(sec):
    # a.bcdefghijk... --> "abcd.efg"
    return str(int(sec * 10**6) / 10**3)

def main():
    print("MODEL NAME, \tBATCH SIZE,\tAVG LATENCY (ms),\tAVG MEM USAGE (MB)")

    parser = argparse.ArgumentParser()
    parser.add_argument('--model_name', type=str)
    parser.add_argument('--num_inference', type=int)
    parser.add_argument('--batch_size', type=int)
    args = parser.parse_args()
    model_name = args.model_name
    num_inference = args.num_inference
    batch_size = args.batch_size
    # train
    if (model_name == "resnet"):
        with torch.no_grad():
            model = models.resnet18(True, True)
            # warmup
            for i in range(50):
                # input
                empty_tensor = torch.zeros(batch_size, 3, 224, 224)
                model(empty_tensor)
            # inference
            inference_times = list()
            for i in range(num_inference):
                # input
                empty_tensor = torch.zeros(batch_size, 3, 224, 224)
                start_time = time.time()
                model(empty_tensor)
                torch.cuda.synchronize()
                end_time = time.time()
                inference_times.append(end_time - start_time)
            str_avg_inf_time = sec_to_ms(sum(inference_times) / len(inference_times))
            print(",".join(["RESNET18", str(batch_size), str_avg_inf_time]))
    elif (model_name == "mobilenet"):
        return None
    elif (model_name == "bert"):
        with torch.no_grad():
            tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
            model = AutoModel.from_pretrained("bert-base-uncased")
            # warmup
            for i in range(50):
                token_list = ["warmup tokens!"] * batch_size
                inputs = tokenizer(token_list, return_tensors="pt")
            # inference
            inference_times = list()
            for i in range(num_inference):
                token_list = ["warmup tokens!"] * batch_size
                inputs = tokenizer(token_list, return_tensors="pt")
                start_time = time.time()
                outputs = model(**inputs)
                torch.cuda.synchronize()
                end_time = time.time()
                inference_times.append(end_time - start_time)
            str_avg_inf_time = sec_to_ms(sum(inference_times) / len(inference_times))
            print(",".join(["BERT-BASE-UNCASED", str(batch_size), str_avg_inf_time]))
    else:
        print("Unidentified model name: {}".format(model_name))
        return
# allocated memory: torch.cuda.memory_allocated() but this keeps returning 0


if __name__ == "__main__":
    main()

