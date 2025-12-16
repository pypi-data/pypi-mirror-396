# Regression Test Suite for Production Readiness

This document describes the comprehensive regression test suite created to track and fix the remaining quality issues identified in the 356-PDF benchmark analysis.

## Test Suite Overview

We've created **6 regression test files** with **22 total tests**, each targeting a specific category of quality issues:

### 1. **test_regression_empty_outputs.rs** - P0 Critical
**Issue**: 11 PDFs (3%) produce <100 characters of output
**Severity**: CRITICAL - Complete extraction failure
**Tests**:
- `test_empty_output_files_have_content()` - Verify all files produce adequate output
- `test_empty_outputs_have_spans()` - Check if span extraction works
- `test_empty_outputs_minimum_chars()` - Expect >500 chars per page

**Files Affected**:
- WXURHXHVCOCL3XIN4PFUPT2OGYFIXYR5.pdf
- 5JWNPTKTIAPTHTEGVKW7WVNBDBKQMRJO.pdf
- QJRUY4FRCDHXZJT5ZAWKMADAMAQUP5R6.pdf
- D45G6SVN7QZSMYJOJGWLKE3MJ6DHTYY5.pdf
- ZC2ELDSYWFVOJZRXTLERXVM7UMXWCWZN.pdf

### 2. **test_regression_replacement_chars.rs** - P1 High
**Issue**: 42 PDFs (12%) still contain U+FFFD after Font fix
**Severity**: MAJOR - Encoding failures
**Progress**: Reduced from 57 to 42 files (26% improvement!)
**Tests**:
- `test_no_replacement_characters()` - Verify no U+FFFD in markdown
- `test_replacement_chars_span_level()` - Check spans for U+FFFD
- `test_specific_problematic_chars()` - Analyze problematic character codes
- `test_font_encoding_used()` - Diagnose font/encoding issues

**Files Affected**:
- YBTLDNWUYL3SLS4NVMFEB3OFUWOZBLA7.pdf
- arxiv_2510.25758v1.pdf
- arxiv_2510.25732v1.pdf
- arxiv_2510.25726v1.pdf
- arxiv_2510.25694v1.pdf
- (and 37 more...)

### 3. **test_regression_word_splitting.rs** - P1 High
**Issue**: 268 PDFs (75%) have word splitting problems
**Severity**: MAJOR - Biggest quality issue!
**Root Cause**: Overly aggressive TJ array offset interpretation
**Tests**:
- `test_no_common_word_splitting()` - Detect split common words
- `test_space_span_ratio()` - Check for excessive space spans (>20% = over-splitting)
- `test_consecutive_short_spans()` - Find suspicious span sequences
- `test_word_length_distribution()` - Verify healthy average word length (4-5 chars)
- `test_specific_word_patterns()` - Test for known splits ("var ious", "cor relation", etc.)

**Files Affected**:
- SEVNFYZBX7VQEWEG5SQQTFZK24PCUDFU.pdf
- ELS4P7L7AQO4WFSJVMCLQZ4HLOQIHFZU.pdf
- LCFQJGJLCOJ56B3YM3XIPRJ7DFUQPTDG.pdf
- RLGNJP7L3BZWPR6KCTTN5I4DIPFSCP3L.pdf
- MMSNF4WV7XLHQFKEQYKHHH7GJPPQJQ7U.pdf
- (and 263 more...)

### 4. **test_regression_control_chars.rs** - P2 Medium
**Issue**: 61 PDFs (17%) contain unexpected control characters
**Severity**: MAJOR - Raw bytes leaking into output
**Tests**:
- `test_no_control_characters_in_output()` - Verify no control chars (ASCII <32 except \n, \r, \t)
- `test_spans_have_no_control_chars()` - Check spans for control chars
- `test_markdown_is_clean_printable()` - Ensure only printable output

**Expected**: Zero control characters in final markdown

### 5. **test_regression_whitespace.rs** - P3 Low
**Issue**: 153 PDFs (43%) have excessive whitespace
**Severity**: MINOR - Cosmetic issue
**Tests**:
- `test_no_excessive_whitespace()` - Detect 3+ consecutive spaces (allow <10 occurrences)
- `test_whitespace_ratio()` - Verify space ratio <30%, newline ratio <15%
- `test_no_trailing_whitespace()` - Check for trailing spaces (<10% of lines)
- `test_paragraph_spacing()` - Normalize 3+ consecutive newlines (<20 occurrences)

**Expected**: Clean, normalized whitespace

### 6. **test_regression_encoding_issues.rs** - P3 Low
**Issue**: 21 PDFs (6%) have encoding issues beyond U+FFFD
**Severity**: MINOR - Various encoding problems (mojibake, invalid Unicode)
**Tests**:
- `test_no_encoding_issues()` - Comprehensive detection (invalid Unicode, mojibake, null bytes, excessive non-ASCII)
- `test_valid_unicode_only()` - Check for invalid Unicode ranges (surrogates, >U+10FFFF)
- `test_no_mojibake()` - Detect common mojibake patterns (Ã©, â€™, etc.)

**Files Affected**:
- arxiv_2510.25765v1.pdf
- arxiv_2510.25522v1.pdf
- arxiv_2510.25332v1.pdf
- arxiv_2510.25701v1.pdf
- arxiv_2510.25264v1.pdf

## Running the Tests

### Run All Regression Tests
```bash
cargo test --release test_regression
```

### Run Specific Test Suite
```bash
# Empty outputs (P0)
cargo test --release --test test_regression_empty_outputs

# Replacement characters (P1)
cargo test --release --test test_regression_replacement_chars

# Word splitting (P1 - biggest issue)
cargo test --release --test test_regression_word_splitting

# Control characters (P2)
cargo test --release --test test_regression_control_chars

# Whitespace (P3)
cargo test --release --test test_regression_whitespace

# Encoding issues (P3)
cargo test --release --test test_regression_encoding_issues
```

### Run Specific Test
```bash
cargo test --release test_no_replacement_characters
cargo test --release test_space_span_ratio
```

## Test Strategy

Each test suite follows this pattern:

1. **Identify**: Use specific PDFs known to exhibit the issue
2. **Diagnose**: Tests that expose the root cause
3. **Verify**: Tests that check the fix works
4. **Prevent**: Regression tests to ensure it stays fixed

Tests are designed to:
- ✅ Be fast (only test first few pages)
- ✅ Be specific (clear failure messages)
- ✅ Be actionable (provide debugging output)
- ✅ Be incremental (can fix one file at a time)

## Current Test Results

As of the latest run:

| Test Suite | Status | Files Affected | Priority |
|-----------|--------|----------------|----------|
| Empty Outputs | ❌ FAIL | 11 (3%) | P0 Critical |
| Replacement Chars | ❌ FAIL | 42 (12%) | P1 High |
| Word Splitting | ❌ FAIL | 268 (75%) | P1 High |
| Control Characters | ❌ FAIL | 61 (17%) | P2 Medium |
| Excessive Whitespace | ❌ FAIL | 153 (43%) | P3 Low |
| Encoding Issues | ❌ FAIL | 21 (6%) | P3 Low |

## Progress Tracking

### Completed ✅
- Font dictionary dereferencing bug fixed
- Reduced U+FFFD from 57 to 42 files (26% improvement)
- Comprehensive test suite created
- Quality analysis framework built

### In Progress 🔄
- Investigating 11 complete extraction failures
- Analyzing remaining U+FFFD cases
- Reviewing TJ array handling for word splitting

### To Do 📝
1. Fix 11 empty output failures (P0)
2. Fix remaining 42 U+FFFD cases (P1)
3. Overhaul TJ array processing to fix word splitting (P1)
4. Filter control characters from output (P2)
5. Improve whitespace normalization (P3)

## Success Criteria for Production

The library will be considered **Production Ready** when:

1. ✅ **Zero** complete extraction failures (currently 11)
2. ✅ **<5%** files with U+FFFD (currently 12%)
3. ✅ **<10%** files with word splitting (currently 75%)
4. ✅ **Zero** control characters in output (currently 17% affected)
5. ✅ **<20%** files with excessive whitespace (currently 43%)
6. ✅ All regression tests passing
7. ✅ Test coverage >80%
8. ✅ Performance: <200ms/page average

## Development Workflow

1. **Pick a failing test** from the priority list
2. **Run the specific test** to see failure details
3. **Debug** using the diagnostic output
4. **Fix** the root cause
5. **Verify** the test now passes
6. **Run full suite** to ensure no regressions
7. **Commit** with test name in commit message

Example:
```bash
# 1. Run failing test
cargo test --release test_empty_output_files_have_content -- --nocapture

# 2. Fix the issue in code

# 3. Verify fix
cargo test --release test_empty_output_files_have_content

# 4. Check no regressions
cargo test --release test_regression

# 5. Commit
git commit -m "fix: resolve empty output for PDF type X (test_empty_output_files_have_content)"
```

## Notes

- Tests are designed to fail initially - this is expected!
- Each test documents the expected behavior
- Debug output saved to /tmp/ for investigation
- Tests use real PDFs from benchmark dataset
- All tests run in <5 seconds for fast iteration

## References

- Quality report: `test_datasets/benchmark_outputs/pdf_oxide/quality_report.json`
- Analysis script: `/tmp/analyze_pdf_quality.py`
- Benchmark tool: `src/bin/benchmark_all_pdfs.rs`
- Original analysis: Previous session summary
