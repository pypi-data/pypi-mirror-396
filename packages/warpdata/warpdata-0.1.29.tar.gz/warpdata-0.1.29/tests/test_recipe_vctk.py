"""
Tests for VCTK recipe.
"""
import pytest
from pathlib import Path
import warpdata as wd


def test_vctk_recipe_basic():
    """Test basic VCTK recipe execution with small sample."""
    # Run with small limit for quick test
    result = wd.run_recipe(
        "vctk",
        "warpdata://audio/vctk-test",
        limit=100,
        vctk_root="/home/alerad/.cache/kagglehub/datasets/pratt3000/vctk-corpus/versions/1/VCTK-Corpus/VCTK-Corpus",
        download_with_kagglehub=False,
        with_materialize=True
    )

    # Verify result structure
    assert 'main' in result
    assert 'subdatasets' in result
    assert 'speakers' in result['subdatasets']

    # Load utterances dataset
    utterances = wd.load("warpdata://audio/vctk-test", as_format="pandas")

    # Verify structure
    assert len(utterances) == 100
    assert 'speaker_id' in utterances.columns
    assert 'utterance_id' in utterances.columns
    assert 'audio_path' in utterances.columns
    assert 'text_path' in utterances.columns
    assert 'text' in utterances.columns
    assert 'duration_sec' in utterances.columns

    # Verify data types
    assert utterances['speaker_id'].dtype == 'object'
    assert utterances['text'].dtype == 'object'

    # Verify no missing values in key columns
    assert utterances['speaker_id'].notna().all()
    assert utterances['text'].notna().all()


def test_vctk_speakers_subdataset():
    """Test VCTK speakers subdataset (different schema - valid use case!)."""
    # Run recipe (reuse from previous test if already exists)
    try:
        speakers = wd.load("warpdata://audio/vctk-test-speakers", as_format="pandas")
    except:
        wd.run_recipe(
            "vctk",
            "warpdata://audio/vctk-test",
            limit=100,
            vctk_root="/home/alerad/.cache/kagglehub/datasets/pratt3000/vctk-corpus/versions/1/VCTK-Corpus/VCTK-Corpus",
            download_with_kagglehub=False,
            with_materialize=True
        )
        speakers = wd.load("warpdata://audio/vctk-test-speakers", as_format="pandas")

    # Verify structure
    assert 'speaker_id' in speakers.columns
    assert 'age' in speakers.columns
    assert 'gender' in speakers.columns
    assert 'accent' in speakers.columns
    assert 'region' in speakers.columns

    # Verify data types
    assert speakers['speaker_id'].dtype == 'object'
    assert speakers['age'].dtype == 'int64'  # Should be int, not string
    assert speakers['gender'].dtype == 'object'
    assert speakers['accent'].dtype == 'object'
    assert speakers['region'].dtype == 'object'

    # Verify gender values
    assert set(speakers['gender'].unique()).issubset({'M', 'F'})

    # Verify accents
    expected_accents = {'English', 'Scottish', 'Irish', 'American', 'Canadian',
                       'Australian', 'NorthernIrish', 'Welsh', 'Indian',
                       'SouthAfrican', 'NewZealand'}
    assert set(speakers['accent'].unique()).issubset(expected_accents)


def test_vctk_join_utterances_speakers():
    """Test joining utterances with speakers (demonstrates different schemas)."""
    # Load both datasets
    try:
        utterances = wd.load("warpdata://audio/vctk-test", as_format="pandas")
        speakers = wd.load("warpdata://audio/vctk-test-speakers", as_format="pandas")
    except:
        wd.run_recipe(
            "vctk",
            "warpdata://audio/vctk-test",
            limit=100,
            vctk_root="/home/alerad/.cache/kagglehub/datasets/pratt3000/vctk-corpus/versions/1/VCTK-Corpus/VCTK-Corpus",
            download_with_kagglehub=False,
            with_materialize=True
        )
        utterances = wd.load("warpdata://audio/vctk-test", as_format="pandas")
        speakers = wd.load("warpdata://audio/vctk-test-speakers", as_format="pandas")

    # Join datasets
    merged = utterances.merge(speakers, on='speaker_id', how='left')

    # Verify join worked
    assert len(merged) == len(utterances)
    assert 'age' in merged.columns
    assert 'gender' in merged.columns
    assert 'accent' in merged.columns
    assert 'region' in merged.columns

    # Test filtering after join
    female_utterances = merged[merged['gender'] == 'F']
    assert len(female_utterances) > 0

    scottish_utterances = merged[merged['accent'] == 'Scottish']
    # May be 0 if small sample doesn't include Scottish speakers


def test_vctk_text_content():
    """Test that text transcriptions are loaded correctly."""
    try:
        utterances = wd.load("warpdata://audio/vctk-test", as_format="pandas")
    except:
        wd.run_recipe(
            "vctk",
            "warpdata://audio/vctk-test",
            limit=100,
            vctk_root="/home/alerad/.cache/kagglehub/datasets/pratt3000/vctk-corpus/versions/1/VCTK-Corpus/VCTK-Corpus",
            download_with_kagglehub=False,
            with_materialize=True
        )
        utterances = wd.load("warpdata://audio/vctk-test", as_format="pandas")

    # Verify text is not empty
    assert all(len(text) > 0 for text in utterances['text'])

    # Verify text files exist
    for text_path in utterances['text_path'].head(10):
        assert Path(text_path).exists()

    # Verify audio files exist
    for audio_path in utterances['audio_path'].head(10):
        assert Path(audio_path).exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
