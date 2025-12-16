# Development Documentation

This directory contains internal development documentation for FurlanSpellChecker.

## Files

### [`COF_Parity_Roadmap.md`](./COF_Parity_Roadmap.md)
**Comprehensive test parity roadmap** tracking the porting process from COF (Perl) to FurlanSpellChecker (Python).

**Contents**:
- Phase-by-phase migration plan (8 phases)
- Test coverage tracking (646 total tests)
- Critical bug tracking and resolution
- Git commit guidelines
- Progress metrics and status

**Current Status**: Phase 5.1 complete (database migration to SQLite)

**Key Sections**:
- 🚨 Critical database corruption resolved (29.2% NULL values in frequencies)
- Phase breakdowns with tasks and success criteria
- Commit history and completed phases
- Remaining work and blockers

---

### [`Database_Migration_Strategy.md`](./Database_Migration_Strategy.md)
**Comprehensive database migration analysis and strategy** - combines investigation, analysis, and implementation plan.

**Contents**:
- **Investigation Process**: Discovery timeline and debugging steps
- **Critical Issue Analysis**: frequencies.sqlite corruption (20,117 accented words)
- **COF Database Comparison**: All 5 databases analyzed
- **Access Pattern Analysis**: Performance characteristics
- **Proposed Solution**: Migration to SQLite format
- **GitHub Releases Strategy**: Distribution without Git LFS limits
- **Migration Plan**: Phase 5.1 and Phase 6 detailed checklist
- **Implementation Guide**: Step-by-step tasks

**Key Findings**:
- 100% of Friulian accented words had NULL frequency (now resolved)
- Root cause: BerkeleyDB → SQLite conversion bug in legacy system
- Solution: Re-export via Perl + migrate to optimized SQLite
- Benefits: Simpler, faster, more reliable, standard SQL tooling

**Recommended Strategy**:
- Format: SQLite for all databases (words, frequencies, errors, elisions)
- Distribution: GitHub Releases (no Git LFS bandwidth limits)
- Priority: All databases migrated to SQLite (complete)
- Timeline: Completed in Phase 5.1 and Phase 6

**Investigation Scripts**:
- `analyze_frequency_db.py` - Database corruption analysis
- `check_cof_frec_direct.pl` - Verify COF original values
- `compare_cof_sqlite.py` - Compare encoding
- `export_frec_to_json.pl` - Export for conversion

---

### [`testing.md`](./testing.md)
**Testing guide and troubleshooting** for running the FurlanSpellChecker test suite.

**Contents**:
- Quick start commands
- Expected test duration and why tests are slow
- VS Code terminal known issues (KeyboardInterrupt, buffering)
- Database requirements
- Debugging tips and CI/CD considerations

**Key Information**:
- Full test suite: **733 tests** in ~11 minutes
- Database loading: 289MB words.sqlite adds startup time
- VS Code background execution can cause spurious interrupts

---

## Quick Links

### For Developers
- **Starting contribution?** Read [`COF_Parity_Roadmap.md`](./COF_Parity_Roadmap.md) first
- **Running tests?** Read [`testing.md`](./testing.md) for gotchas
- **Database issues?** Check [`Database_Strategy_Analysis.md`](./Database_Strategy_Analysis.md)
- **Need test data?** See `../../tests/fixtures/`

### For Maintainers
- **Release process?** See [`../dictionaries.md`](../dictionaries.md)
- **GitHub releases?** See [`../github-releases.md`](../github-releases.md)

---

## Status Dashboard

| Metric | Value | Status |
|--------|-------|--------|
| **Total Tests** | 733 | ✅ Complete |
| **Passing Tests** | 733/733 | ✅ 100% |
| **Current Phase** | 5.1 Complete | ✅ Done |
| **Critical Bugs** | 0 | ✅ Resolved |
| **Database Status** | SQLite | ✅ Migrated |

**Last Updated**: 2025-11-28

---

## Contributing

When working on test parity:

1. ✅ **Always** check the roadmap before starting work
2. ✅ **Follow** the git commit guidelines in the roadmap
3. ✅ **Update** the roadmap after completing each phase
4. ✅ **Document** any new discoveries or bugs
5. ✅ **Test** against COF behavior (100% parity required)

**Critical Policy**: Any difference between COF and FurlanSpellChecker behavior is a **CRITICAL BUG** - see roadmap for details.
