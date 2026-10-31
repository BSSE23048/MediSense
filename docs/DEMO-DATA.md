# Runtime data and portfolio demonstrations

The SQLite database contains user/report/chat runtime records and does not belong in source control. The storage service creates the required tables on startup, so fresh installations do not need a committed database.

Use synthetic documents and accounts in demonstrations. Never upload personal medical reports, real account records, passwords/hashes or chat histories as portfolio fixtures.

Removing a file from the current tree does not remove copies in Git history. The owner must establish whether previously committed records are synthetic, review any real-data exposure, and coordinate remediation where necessary. No history rewrite or production data deletion is performed by this change.

Before deploying a release without the tracked database, confirm that real runtime data is backed up and stored on the intended persistent volume outside the deployment source tree.

The storage-bootstrap CI job tests fresh empty database creation and preservation of an existing synthetic record. It does not validate OCR, medical answers, RAG grounding, voice providers or production privacy.
