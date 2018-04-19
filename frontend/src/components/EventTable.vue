<template>
  <b-container fluid>
    <!-- Search filters -->
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
        <b-form-group horizontal label="Older then" class="mb-3">
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
  </b-container>
</template>

<script>
import axios from 'axios';

const headers = [ 'event_id', 'aloha_id', 'platform', 'key', 'value', 'location', 'pairs', 'timestamp' ]
const SERVER_URL = "http://localhost:9999"

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
      isBusy: false
    }
  },

  mounted() {
    this.maxId = 0;
    this.needToUpdate = false;
    setInterval(function () {
      this.eventProvider();
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
     refresh (ctx) {
       if (this.needToUpdate) {
         this.$refs.table.refresh();
         this.needToUpdate = false;
       }
     },

     updateTable (ctx) {
       // Update only after timeout
       clearTimeout(this.timeout);
       this.timeout = setTimeout( () => {
         this.eventProvider(ctx);
         this.$refs.table.refresh();
       }, 350);
     },
     eventProvider (ctx) {
      let params = '?aloha_id=' + this.alohaId + '&key=' + this.key + '&value='
      + this.value + '&limit=' + this.limit + '&timestamp=' + this.timestamp
      let url = SERVER_URL + '/events/' + params
      let promise = axios.get(url)

      return promise.then((response) => {
        const items = response.data.map(toObject);
        var maxId = Math.max.apply(Math,items.map(function(o){return Number(o.event_id);}));
        if (maxId > this.maxId) {
          this.maxId = maxId;
          this.needToUpdate = true;
        }
        return (items || [])
      }).catch(error => {
        console.log(error);
        return []
      })
    },
  }
}
</script>
