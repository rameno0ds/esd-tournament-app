<template>
  <div>
    <nav>
      <router-link to="/">Home</router-link>
      <router-link to="/tournament">Tournaments</router-link>
      <router-link to="/dispute">Disputes</router-link>
    </nav>
    <router-view />
  </div>
</template>

<style>
nav {
  display: flex;
  gap: 15px;
  justify-content: center;
  padding: 10px;
  background: #eee;
}
</style>
