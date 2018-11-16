1. [X] Store and access abstract “data objects” across storage nodes using RAID-6 for fault-tolerance
2. [X] Include mechanisms to determine failure of storage nodes
3. [X] Carry out rebuild of lost redundancy at a replacement storage node.
4. [ ] In the objective “1” above, it is deliberately vague as to what data objects mean. You can consider them as something like x-MB data chunks. However, actual files may be much smaller, or larger than the quantum of data which is treated as an object in the system. In a practical system, it is necessary to accommodate real files of arbitrary size, taking into account issues like RAID mapping, etc.
5. [ ] Instead of using folders to emulate nodes, extend the implementation to work across multiple (virtual) machines to realize a peer-to-peer RAIN.
6. [ ] Support mutable files, taking into account update of the content, and consistency issues.
7. [ ] Support larger set of configurations (than just 6+2, using a more full-fledged implementation).
8. [ ] Optimize the computation operations.
9. [ ] Anything else (please feel free to discuss during the course of the project)