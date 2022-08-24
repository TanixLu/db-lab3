<template>
  <el-menu router mode="horizontal" :default-active="$route.path">
    <el-menu-item index="/client">客户管理</el-menu-item>
    <el-submenu index="">
      <template #title>账户管理</template>
      <el-menu-item index="/saving_account">储蓄账户</el-menu-item>
      <el-menu-item index="/checking_account">支票账户</el-menu-item>
    </el-submenu>
    <el-menu-item index="/loan">贷款管理</el-menu-item>
    <el-menu-item index="/statistics">业务统计</el-menu-item>
  </el-menu>
</template>

<script>
export default {
  name: "AppHeader"
}
</script>
