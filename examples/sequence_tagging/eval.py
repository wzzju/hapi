#   Copyright (c) 2019 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
SequenceTagging eval structure
"""

from __future__ import division
from __future__ import print_function

import io
import os
import sys
import math
import argparse
import numpy as np

work_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(work_dir, "../"))

from paddle.incubate.hapi.model import set_device, Input
from paddle.incubate.hapi.text.sequence_tagging import SeqTagging, ChunkEval, LacLoss
from paddle.incubate.hapi.text.sequence_tagging import LacDataset, LacDataLoader
from paddle.incubate.hapi.text.sequence_tagging import check_gpu, check_version
from paddle.incubate.hapi.text.sequence_tagging import PDConfig

import paddle.fluid as fluid
from paddle.fluid.layers.utils import flatten


def main(args):
    place = set_device(args.device)
    fluid.enable_dygraph(place) if args.dynamic else None

    inputs = [
        Input(
            [None, None], 'int64', name='words'), Input(
                [None], 'int64', name='length'), Input(
                    [None, None], 'int64', name='target')
    ]
    labels = [Input([None, None], 'int64', name='labels')]

    dataset = LacDataset(args)
    eval_dataset = LacDataLoader(args, place, phase="test")

    vocab_size = dataset.vocab_size
    num_labels = dataset.num_labels
    model = SeqTagging(args, vocab_size, num_labels, mode="test")

    model.mode = "test"
    model.prepare(
        metrics=ChunkEval(num_labels),
        inputs=inputs,
        labels=labels,
        device=place)
    model.load(args.init_from_checkpoint, skip_mismatch=True)

    eval_result = model.evaluate(
        eval_dataset.dataloader, batch_size=args.batch_size)
    print("precison: %.5f" % (eval_result["precision"][0]))
    print("recall: %.5f" % (eval_result["recall"][0]))
    print("F1: %.5f" % (eval_result["F1"][0]))


if __name__ == '__main__':
    args = PDConfig(yaml_file="sequence_tagging.yaml")
    args.build()
    args.Print()

    use_gpu = True if args.device == "gpu" else False
    check_gpu(use_gpu)
    check_version()
    main(args)
