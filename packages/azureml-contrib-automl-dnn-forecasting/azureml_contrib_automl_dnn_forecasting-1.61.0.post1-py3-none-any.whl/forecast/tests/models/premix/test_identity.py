import dataclasses as dc
import random

import pytest
import torch

import forecast.models.premix as premix
from forecast.models.common import TensorShapeException


@pytest.mark.parametrize("input_channels", [1, 5, 10, 20])
def test_premix_identity_config(input_channels):
    config = premix.IdentityPremixConfig(input_channels=input_channels)
    iden = config.create_premix()  # ensure we can create premix
    assert iden.receptive_field == 1
    assert iden.output_channels == input_channels
    assert iden.is_future_conditioned == False

    d = dc.asdict(config)

    for cls in [premix.IdentityPremixConfig, premix.AbstractPremixConfig]:
        config_new = cls.fromdict(d)
        assert config == config_new


# test 0 input channels and output != input for identity
def test_premix_identity_config_failure_0_input_channel():
    with pytest.raises(ValueError):
        config = premix.IdentityPremixConfig(input_channels=0)


@pytest.mark.parametrize("input_channels", [1, 5, 10, 20])
@pytest.mark.parametrize("batch_size", [1, 4, 128])
@pytest.mark.parametrize("ts_len", [1, 90])
def test_premix_identity(input_channels, batch_size, ts_len):
    config = premix.IdentityPremixConfig(input_channels=input_channels)
    iden = config.create_premix()

    tensor = torch.rand(batch_size, input_channels, ts_len)
    out = iden(tensor)
    assert torch.all(out == tensor)
