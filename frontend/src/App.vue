<template>
  <div id="app">
    <img src="./assets/logo.png" class="mb-3" width="200px">
    <h1> Async Aloha service</h1>
    <hr/>
    <event-table></event-table>
  </div>
</template>

<script>
import EventTable from './components/EventTable'

export default {
  name: 'app',
  components: {
    EventTable
  }
}

</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
  font-size: 0.9rem;
}

#app .badge-pill{
  font-size: 0.8rem;
}
</style>
