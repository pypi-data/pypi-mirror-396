"""Test that the GutsBase configuration can be saved to and loaded from a file.

The configuration model lives in ``guts_base/sim/config.py`` and is based on the
``pymob`` configuration system.  The base ``pymob`` ``Config`` class provides a
``save`` method that writes a ``settings.cfg`` file and can be re‑instantiated
by passing the file path to ``Config``.  This test verifies that a round‑trip
(save → load) preserves the configuration data.

The test does not inspect individual fields – it only checks that the two
configuration objects are equivalent after serialization/deserialization.
"""

from pymob.sim.config import Config


def test_save_and_load_roundtrip(tmp_path):
    """A Config instance should survive a save‑then‑load cycle."""
    # Create a default configuration.
    original_cfg = Config()

    # ``save`` writes the configuration; ``force=True`` skips the
    # overwrite prompt.
    original_cfg.save(tmp_path / "settings.cfg", force=True)

    # Reload the configuration from the file we just wrote.
    loaded_cfg = Config(str(tmp_path / "settings.cfg"))

    # ``model_dump`` returns a plain‑dict representation of the model.
    # Equality of these dicts confirms that the configuration survived the
    # round‑trip unchanged.
    # reslts interpolation contains nans
    assert loaded_cfg.guts_base.model_dump(exclude="results_interpolation") == original_cfg.guts_base.model_dump(exclude="results_interpolation")
