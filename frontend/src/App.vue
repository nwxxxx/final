<!-- 模板部分 -->
<template>
  <!-- 根元素，id为app，用于全局样式定位 -->
  <div id="app">
    <!-- 使用Element UI的容器组件，设置高度为视口高度 -->
    <el-container style="height: 100vh;">
      <!-- 使用Element UI的侧边栏组件，宽度设置为200px，背景颜色设置为#545c64 -->
      <el-aside width="200px" style="background-color: #545c64;">
        <!-- 引入并注册名为navi的子组件，用于显示导航菜单 -->
        <navi></navi>
      </el-aside>
      <!-- 使用Element UI的主内容区域组件 -->
      <el-main>
        <!-- 路由视图，用于显示当前路由匹配的组件 -->
        <router-view></router-view>
      </el-main>
    </el-container>
  </div>
</template>

<!-- 脚本部分 -->
<script>
// 导入Navi组件，该组件位于./components/Navi.vue
import Navi from './components/Navi.vue'

// 定义根组件App
export default {
  name: 'App', // 组件名称为App
  components: { // 注册局部组件
    Navi // 注册的组件名为Navi
  }
}
</script>

<!-- 样式部分 -->
<style>
/* 设置根元素app的字体、字体平滑和文字颜色 */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

/* 设置侧边栏的文字颜色为白色 */
.el-aside {
  color: white;
}
</style>