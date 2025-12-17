prsync
来源：https://github.com/nathanhaigh/parallel-rsync
用法
如果您的命令如下所示：rsync

```bash
rsync \
  --times --recursive --progress \
  --exclude "raw_reads" --exclude ".snakemake" \
  user@example.com:/my_remote_dir/ /my_local_dir/
```
只需替换此脚本的可执行文件：rsync
```bash
./prsync \
  --times --recursive --progress \
  --exclude "raw_reads" --exclude ".snakemake" \
  user@example.com:/my_remote_dir/ /my_local_dir/
  ```

并行作业数
默认情况下，脚本将为计算机上的每个处理器使用 1 个并行作业。 这是由确定的，如果失败，我们将回退到并行作业来传输文件。 
可以通过使用作为脚本的第一个命令行参数来覆盖此行为：```nproc 10 --parallel```
```bash
./prsync \
  --parallel=20 \
  --times --recursive --progress \
  --exclude "raw_reads" --exclude ".snakemake" \
  user@example.com:/my_remote_dir/ /my_local_dir/
```