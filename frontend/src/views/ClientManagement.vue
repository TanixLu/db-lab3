<template>
  <el-row justify="space-around">

    <el-col :span="6">
      <el-form
        label-position="left"
        label-width="110px"
        size="small"
      >
        <el-form-item v-for="field in client_fields" :key="field.name" :label="field.label">
          <el-input v-model="field.search_ref"/>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchClient()">查询</el-button>
        </el-form-item>
      </el-form>
    </el-col>

    <el-col :span="6">
      <div class="pagination-block">
        <el-table :data="info.results" border @row-click="fillInput" size="small">
          <el-table-column prop="id" label="身份证号"/>
          <el-table-column prop="name" label="姓名"/>
        </el-table>
        <el-pagination
            layout="prev, pager, next"
            :page-size="8"
            :page-count="pageCount"
            v-model:currentPage="currentPage"
        />
      </div>
    </el-col>

    <el-col :span="9">
      <el-form
        label-position="left"
        label-width="110px"
        size="small"
      >
        <el-form-item v-for="field in client_fields" :key="field.name" :label="field.label">
          <el-input v-model="field.input_ref"/>
        </el-form-item>
        <el-form-item>
          <el-button type="success" @click="addClient">添加</el-button>
          <el-button type="warning" @click="updateClient">更新</el-button>
          <el-popconfirm
              title="确定要删除该客户吗？"
              cancel-button-type="primary"
              cancel-button-text="否"
              confirm-button-type="danger"
              confirm-button-text="是"
              @confirm="deleteClient"
          >
            <template #reference>
              <el-button type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </el-form-item>
      </el-form>
    </el-col>

  </el-row>
</template>


<script>
import axios from 'axios'
import {ElMessage} from 'element-plus'

const client_fields = [
  {'name': 'id', 'label': '身份证号'},
  {'name': 'name', 'label': '姓名',},
  {'name': 'phone_number', 'label': '电话号码'},
  {'name': 'address', 'label': '地址'},
  {'name': 'contact_name', 'label': '联系人姓名'},
  {'name': 'contact_phone_number', 'label': '联系人电话号码'},
  {'name': 'contact_email', 'label': '联系人电子邮箱'},
  {'name': 'contact_relationship', 'label': '联系人关系'}
]
client_fields.forEach(field => field['search_ref'] = '')
client_fields.forEach(field => field['input_ref'] = '')

const api_url = 'http://localhost:8000/api/'
const client_url = api_url + 'client/'

const auth_config = {auth: {username: 'tanix', password: '1234'}}

export default {
  name: "ClientManagement",
  components: {
  },
  data() {
    return {
      info: '',
      client_fields,
      currentPage: 1,
      pageCount: 0,
      query_url: '',
    }
  },
  mounted() {
    this.searchClient()
  },
  watch: {
    currentPage: async function (newPage) {
      this.info = (await axios.get(this.query_url + 'page=' + newPage.toString(), auth_config)).data
      this.pageCount = Math.ceil(this.info.count / 8)
    }
  },
  methods: {
    searchClient: async function () {
      let vm = this
      vm.currentPage = 1
      vm.query_url = client_url + '?'
      client_fields.forEach(field => {
        if(field.search_ref)
          vm.query_url += field.name + '=' + field.search_ref + '&'
      })
      vm.info = (await axios.get(vm.query_url, auth_config)).data
      vm.pageCount = Math.ceil(vm.info.count / 8)
    },

    fillInput: function(client) {
      this.client_fields.forEach(field => field.input_ref = client[field.name])
    },

    addClient: function () {
      let data = {}
      client_fields.forEach(field => data[field.name] = field.input_ref)
      axios.post(client_url, data, auth_config)
        .then(response => {
          if(response.status === 201){
            ElMessage({
              message: '添加成功',
              type: 'success'
            })
          }
        })
        .catch(error => {
          console.log(error)
          ElMessage({
            message: '添加失败',
            type: 'error'
          })
        })
    },

    updateClient: function () {
      let data = {}
      client_fields.forEach(field => data[field.name] = field.input_ref)
      axios.put(client_url + client_fields[0].input_ref + '/', data, auth_config)
        .then(response => {
          if(response.status === 200){
            ElMessage({
              message: '更新成功',
              type: 'success'
            })
          }
        })
        .catch(error => {
          console.log(error)
          ElMessage({
            message: '更新失败',
            type: 'error'
          })
        })
    },

    deleteClient: function () {
      axios.delete(client_url + client_fields[0].input_ref + '/', auth_config)
        .then(response => {
          if(response.status === 204){
            ElMessage({
              message: '删除成功',
              type: 'success'
            })
          }
        })
        .catch(error => {
          console.log(error)
          ElMessage({
            message: '删除失败',
            type: 'error'
          })
        })
    }
  }
}
</script>
