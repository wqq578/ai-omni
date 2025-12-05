#!/bin/bash

# 获取所有节点名称
nodes=$(kubectl get nodes  -l accelerator=dcu| awk '{print $1}')
#nodes=$(kubectl get po -n kube-system -l app.kubernetes.io/name=dcu-exporter -o json | jq -r '.items[].spec.nodeName')
#nodes=$(kubectl get nodes  -l accelerator=deepseek| awk '{print $1}')
# 遍历节点名称并检查是否能够 ping 通
#for node in $nodes; do
#  echo -n "$node " && ssh "$node" "hy-smi --showdriverversion | grep 'Driver Version' | awk '{print $3}' "
#done

# 手动指定节点名称，使用换行分隔
#nodes=""


for node in $nodes; do
  # 获取 Driver Version，并忽略错误信息
  driver_version=$(ssh "$node" "/opt/hyhal/bin/hy-smi --showdriverversion | grep 'Driver Version' | awk '{print \$3}'" 2>/dev/null)

  # 获取 Card Series，并忽略错误信息
  card_series=$(ssh "$node" "/opt/hyhal/bin/hy-smi -a | grep 'Card Series' | awk '{print \$NF}' | head -n 1" 2>/dev/null)

  # 如果 driver_version 或 card_series 为空，则设置默认值为 "N/A"
  driver_version=${driver_version:-N/A}
  card_series=${card_series:-N/A}
  # 格式化输出
  printf "%-20s %-10s %s\n" "$node" "$driver_version" "$card_series"

  # 获取 Driver Version，并忽略错误信息
  driver_version=$(ssh "$node" "rocm-smi --showdriverversion  |grep 'Driver version' | awk '{print \$3}'" 2>/dev/null)

  # 获取 Card Series，并忽略错误信息
  card_series=$(ssh "$node" "rocm-smi -a | grep 'Card Series' | awk '{print \$NF}' | head -n 1" 2>/dev/null)

  # 如果 driver_version 或 card_series 为空，则设置默认值为 "N/A"
  driver_version=${driver_version:-N/A}
  card_series=${card_series:-N/A}
  # 格式化输出
  printf "%-20s %-10s %s\n" "$node" "$driver_version" "$card_series"
done

#for node in $nodes; do
#  # 获取 Driver Version，并忽略错误信息
#  driver_version=$(ssh "$node" "rocm-smi --showdriverversion  |grep 'Driver version' | awk '{print \$3}'" 2>/dev/null)
#
#  # 获取 Card Series，并忽略错误信息
#  card_series=$(ssh "$node" "rocm-smi -a | grep 'Card Series' | awk '{print \$NF}' | head -n 1" 2>/dev/null)
#
#  # 如果 driver_version 或 card_series 为空，则设置默认值为 "N/A"
#  driver_version=${driver_version:-N/A}
#  card_series=${card_series:-N/A}
#
#  # 格式化输出
#  printf "%-20s %-10s %s\n" "$node" "$driver_version" "$card_series"
#done