# GitHub listing and social preview

The README, package description, descriptive headings and image alt text are ready
for public discovery. There are no invented star counts, package-registry badges,
customer claims or hosted websites. Discoverability does not guarantee traffic.

`repository-details.json` contains the prepared About description and topics.
Repository files do not automatically update the GitHub About box. Apply them
using your own authenticated GitHub CLI account with repository admin permission:

```sh
python scripts/configure_repository.py --dry-run
python scripts/configure_repository.py
```

Existing topics are preserved. This script does not change repository visibility,
branch protections or unrelated settings. `assets/banner.svg` is editable artwork
rendered in the README. A ready-to-upload PNG is included in the delivery bundle;
GitHub Social preview settings require a supported raster image rather than SVG.
Uploading that preview is a separate repository-settings action.
