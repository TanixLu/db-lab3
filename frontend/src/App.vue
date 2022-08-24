<template>
  <el-container>
    <el-header><app-header/></el-header>
    <el-main style="margin: 25px"><router-view/></el-main>
  </el-container>
</template>

<script>
import AppHeader from "@/components/AppHeader";

export default {
  name: 'App',
  components: {
    AppHeader,
  },
  computed: {
    isHome() {
      return this.$route.name in window
    }
  }
};
</script>
