<!-- ---
!-- Timestamp: 2026-01-02 15:00:02
!-- Author: ywatanabe
!-- File: /home/ywatanabe/.claude/commands/no-long-term-memory.md
!-- --- -->

# No long-term memory
The user has deficits in long-term memory. Thus, processes should be documented and scripted in an well-organized manner.

# Automated Setup
Regarding setup,
1. Never include, or minimize, manual steps in installation as much as possible.
2. Organize installation scripts
3. Makefile should be a thin dispatcher and delegate actual logics to downstream scripts.
4. Show appropriate warning and error with guidance and hints
5. Switch environment using `.env.{dev,prod}` and `./deployment` scripts
6. In short, make everything clean for administrator not to rely on their long-term memory capabilities. 
7. Problems, notifications, and so on must be shwon in `make status` - this must be a reliable device for loading necessary information to administrator's short-term memory.

<!-- EOF -->