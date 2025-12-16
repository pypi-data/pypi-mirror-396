def test_discover_provider_fallbacks():
    from warpdata.modules.registry import get_provider_class

    cls = get_provider_class("warp.dataset.gsm8k")
    assert cls is not None
    assert cls.__name__ == "GSM8KModule"

    cls = get_provider_class("warp.dataset.gsm8k_symbolized")
    assert cls is not None
    assert cls.__name__ == "GSM8KSymbolizedModule"

    cls = get_provider_class("warp.dataset.gsm8k_symbolized_steps")
    assert cls is not None
    assert cls.__name__ == "GSM8KSymbolizedStepsModule"

    cls = get_provider_class("warp.dataset.logician")
    assert cls is not None
    assert cls.__name__ == "LogicianModule"

