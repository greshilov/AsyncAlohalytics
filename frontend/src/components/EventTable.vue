<template>
  <b-container fluid>
    <!-- Search filters -->
    <!-- Alert -->
    <b-container class="fullscreen">
      <b-alert
        :show="dismissCountdown"
        ref="alert"
        dismissible
        variant="success"
        class="alert-fixed">Statistic recieved!</b-alert>
    </b-container>
    <b-row>
      <b-col md="4" class="my-1">
        <b-form-group horizontal label="Aloha Id" class="mb-3">
          <b-input-group>
            <b-form-input v-model="alohaId" placeholder="Type to search" @input="updateTable"/>
            <b-input-group-append>
              <b-btn :disabled="!alohaId" @click="alohaId = ''">Clear</b-btn>
            </b-input-group-append>
          </b-input-group>
        </b-form-group>
      </b-col>

      <b-col md="4" class="my-1">
        <b-form-group horizontal label="Key" class="mb-3">
          <b-input-group>
            <b-form-input v-model="key" placeholder="Type to search" @input="updateTable"/>
            <b-input-group-append>
              <b-btn :disabled="!key" @click="key = ''">Clear</b-btn>
            </b-input-group-append>
          </b-input-group>
        </b-form-group>
      </b-col>
      <b-col md="4" class="my-1">
        <b-form-group horizontal label="Value" class="mb-3">
          <b-input-group>
            <b-form-input v-model="value" placeholder="Type to search" @input="updateTable"/>
            <b-input-group-append>
              <b-btn :disabled="!value" @click="value = ''">Clear</b-btn>
            </b-input-group-append>
          </b-input-group>
        </b-form-group>
      </b-col>
    </b-row>
    <!-- Limit and timestamp -->
    <b-row class="justify-content-right">
      <b-col md="4" class="my-1">
        <b-form-group horizontal label="Newer than" class="mb-3">
          <b-input-group>
            <b-form-select v-model="timestamp" @change="updateTable">
              <option slot="default" :value="'30 minutes'">30 minutes</option>
              <option :value="'6 hours'">6 hours</option>
              <option :value="'1 day'">1 day</option>
              <option :value="''">All time</option>
            </b-form-select>
          </b-input-group>
        </b-form-group>
      </b-col>
      <b-col md="4" class="my-1">
        <b-form-group horizontal label="Limit" class="mb-0">
          <b-input-group>
            <b-form-select v-model="limit" @change="updateTable">
              <option slot="default" :value="5">5</option>
              <option :value="10">10</option>
              <option :value="30">30</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </b-form-select>
          </b-input-group>
        </b-form-group>
      </b-col>
    </b-row>

    <b-table ref="table" striped hover :busy.sync="isBusy" :items="eventProvider">
      <template slot="pairs" slot-scope="data">
        <b-list-group v-for="value, key in data.value" class="mb-1">
          <b-list-group-item class="d-flex justify-content-between align-items-center">
              {{key}}
              <b-badge variant="primary" pill>{{value | trim }}</b-badge>
          </b-list-group-item>
        </b-list-group>
      </template>
      <template slot="location" slot-scope="data">
        <b-list-group v-for="value, key in data.value" class="mb-1">
          <b-list-group-item class="d-flex justify-content-between align-items-center">
              {{key}}
              <b-badge variant="primary" pill>{{value | trim }}</b-badge>
          </b-list-group-item>
        </b-list-group>
      </template>
    </b-table>
    <b-row class="mb-3 justify-content-md-center">
      <b-pagination align="center" :total-rows="totalRows" :per-page="limit" v-model="currentPage" class="my-0" @input="reloadTable" />
    </b-row>
  </b-container>
</template>

<script>
import axios from 'axios';

const headers = [ 'event_id', 'aloha_id', 'platform', 'key', 'value', 'location', 'pairs', 'timestamp' ]

function toObject(event) {
  var obj = {};
  headers.forEach( (header, index) => {
    obj[header] = event[index];
  });
  return obj;
}

export default {
  data () {
    return {
      alohaId: "",
      key: "",
      value: "",
      timestamp: "",
      limit: 30,
      isBusy: false,
      currentPage: 1,
      totalRows: 0,
      dismissCountdown: 0,
      dismissSeconds: 2
    }
  },

  mounted() {
    this.maxId = 0;
    setInterval(function () {
      this.refresh();
    }.bind(this), 3000);
  },

  filters: {
    trim: function (value) {
      // Check if float
      if (Number(value) == value) {
        return  Math.round(value * 10e5) / 10e5;
      }
      return value
    }
  },

  methods: {
     async refresh (ctx) {
       const newMaxId = await this.getMaxId();
       if (newMaxId > this.maxId) {
         this.maxId = newMaxId;
         this.eventProvider(ctx);
         this.$refs.table.refresh();
         this.dismissCountdown = this.dismissSeconds;
         this.$refs.alert.showChanged();
       }
     },

     reloadTable (ctx) {
       this.eventProvider(ctx);
       this.$refs.table.refresh();
     },

     updateTable (ctx) {
       // Update only after timeout
       clearTimeout(this.timeout);
       this.timeout = setTimeout( () => {
         this.reloadTable()
         this.currentPage = 1;
       }, 350);
     },

     getMaxId (ctx) {
       let url = '/events/max/'
       let promise = axios.get(url)
       return promise.then((response) => {
         return Number(response.data)
       }).catch(error => {
         console.log(error);
         return 0
       })
     },

     eventProvider (ctx) {
      let params = '?aloha_id=' + this.alohaId + '&key=' + this.key + '&value='
      + this.value + '&limit=' + this.limit + '&timestamp=' + this.timestamp
      + '&offset=' + (this.currentPage - 1) * this.limit
      let url = '/events/' + params
      let promise = axios.get(url)
      return promise.then((response) => {
        const items = response.data.events.map(toObject);
        this.totalRows = Number(response.data.count);
        return (items || [])
      }).catch(error => {
        console.log(error);
        return []
      })
    },
  }
}
</script>


<style>

div.fullscreen {
  position: absolute;
  width:100%;
  top: 0;
  left: 0;
}

.alert.alert-fixed {
  position: fixed;
  top: 5px;
  left:2%;
  width: 100%;
  z-index: 1000;
}
</style>
