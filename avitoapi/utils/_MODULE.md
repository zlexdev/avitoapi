# utils/

Catch-all for cross-cutting utility seams that don't fit any other
package. W1 only ships `utils/proxy/` (proxy transport ABC).

Sub-packages are loaded lazily — don't add anything heavy at this level.
