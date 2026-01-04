---
description: Syncronize local changes with remote repository (Commit & Push)
---

1. Check the current status of the repository to see what files have changed.
   ```bash
   git status
   ```

2. Add all changed files to the staging area.
   ```bash
   git add .
   ```

3. Commit the changes with a descriptive message. If the user provided a message, use it. Otherwise, generate a concise and descriptive message based on the changes.
   ```bash
   git commit -m "[Your descriptive message here]"
   ```

4. Push the changes to the remote repository.
   ```bash
   git push origin main
   ```

5. Verify that the push was successful.
   ```bash
   git status
   ```
