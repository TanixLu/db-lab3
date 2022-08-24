<template>
  <el-row justify="space-around">

    <el-col :span="5">
      <el-form
        label-position="left"
        label-width="110px"
        size="small"
      >
        <el-form-item v-for="field in client_branch_fields" :key="field.name" :label="field.label">
          <el-input v-model="field.search_ref"/>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchCheckingAccount()">查询</el-button>
        </el-form-item>
      </el-form>
    </el-col>

    <el-col :span="8">
      <div class="pagination-block">
        <el-table :data="info.results" border @row-click="fillInput" size="small">
          <el-table-column prop="client_id" label="身份证号"/>
          <el-table-column prop="branch_name" label="支行名"/>
          <el-table-column prop="checking_account_id" label="支票账户号"/>
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
        <el-form-item v-for="field in input_fields" :key="field.name" :label="field.label">
          <el-input v-model="field.input_ref"/>
        </el-form-item>
        <el-form-item>
          <el-dialog
            v-model="openDialog"
            title="开户确认"
            width="30%"
          >
            <span>
              <el-descriptions :column="1" border>
                <el-descriptions-item v-for="i in add_indices" :label="input_fields[i].label"
                                      :key="input_fields[i].name" width="110px">
                  {{ input_fields[i].input_ref }}
                </el-descriptions-item>
              </el-descriptions>
            </span>
            <template #footer>
              <span class="dialog-footer">
                <el-button @click="openDialog = false">取消</el-button>
                <el-button type="primary" @click="openCheckingAccount">确认</el-button>
              </span>
            </template>
          </el-dialog>
          <el-button type="success" @click="openDialog = true">开户</el-button>
          <el-button type="warning" @click="updateCheckingAccount">更新</el-button>
          <el-popconfirm
            :title="'确认要删除支票账户' + input_fields[3].input_ref + '吗？'"
            cancel-button-type="primary"
            cancel-button-text="否"
            confirm-button-type="danger"
            confirm-button-text="是"
            @confirm="deleteCheckingAccount"
          >
            <template #reference>
              <el-button type="danger">销户</el-button>
            </template>
          </el-popconfirm>
        </el-form-item>
      </el-form>
    </el-col>

  </el-row>
</template>


<script>
import axios from "axios";
import {ElMessage} from "element-plus";

const client_branch_fields = [
  {'name': 'client_id', 'label': '身份证号'},
  {'name': 'branch_name', 'label': '支行名'},
  {'name': 'checking_account_id', 'label': '支票账户号'},
]
client_branch_fields.forEach(field => field['search_ref'] = '')

const input_fields = [
  {'name': 'client_id', 'label': '身份证号'},
  {'name': 'client_name', 'label': '姓名'},
  {'name': 'branch_name', 'label': '支行名'},
  {'name': 'checking_account_id', 'label': '支票账户号'},
  {'name': 'balance', 'label': '余额'},
  {'name': 'overdraft', 'label': '透支额'},
  {'name': 'staff_id', 'label': '负责人身份证号'},
  {'name': 'open_date', 'label': '开户日期'},
  {'name': 'last_access_date', 'label': '上次访问日期'},
]
input_fields.forEach(field => field['input_ref'] = '')
const add_indices = [0, 2, 5, 6]
const update_indices = [3, 4, 5, 6]

const api_url = 'http://localhost:8000/api/'

const auth_config = {auth: {username: 'tanix', password: '1234'}}

export default {
  name: "CheckingAccountManagement",
  data() {
    return {
      client_branch_fields,
      input_fields,
      add_indices,
      info: '',
      query_url: api_url + 'client_branch/?',
      currentPage: 1,
      pageCount: 0,
      openDialog: false,
    }
  },
  mounted() {
    this.searchCheckingAccount()
  },
  watch: {
    currentPage: async function (newPage) {
      this.info = (await axios.get(this.query_url + 'page=' + newPage.toString(), auth_config)).data
      this.pageCount = Math.ceil(this.info.count / 8)
    }
  },
  methods: {
    searchCheckingAccount: async function () {
      let vm = this
      vm.currentPage = 1
      vm.query_url = api_url + 'client_branch/?'
      client_branch_fields.forEach(field => {
        if(field.search_ref)
            vm.query_url += field.name + '=' + field.search_ref + '&'
      })
      vm.info = (await axios.get(vm.query_url, auth_config)).data
      vm.pageCount = Math.ceil(this.info.count / 8)
    },

    fillInput: function (client_branch) {
      let vm = this
      vm.input_fields[0].input_ref = client_branch['client_id']
      axios.get(api_url + 'client/' + client_branch['client_id'] + '/', auth_config)
        .then(response => vm.input_fields[1].input_ref = response.data['name'])

      vm.input_fields[2].input_ref = client_branch['branch_name']

      if(client_branch['checking_account_id']){
        vm.input_fields[3].input_ref = client_branch['checking_account_id']
        axios.get(api_url + 'checkingaccount/' + client_branch['checking_account_id'] + '/', auth_config)
          .then(response => {
            vm.input_fields[4].input_ref = response.data['balance']
            vm.input_fields[5].input_ref = response.data['overdraft']
            vm.input_fields[6].input_ref = response.data['staff_id']
            vm.input_fields[7].input_ref = response.data['open_date']
            vm.input_fields[8].input_ref = response.data['last_access_date']
          })
      }
      else for(let i = 3; i <= 8; i++) vm.input_fields[i].input_ref = ''
    },

    openCheckingAccount: function () {
      this.openDialog = false
      let data = {}
      add_indices.forEach(i => data[input_fields[i].name] = input_fields[i].input_ref)
      axios.post(api_url + 'client_branch/open_checking_account/', data, auth_config)
          .then(response => {
            if(response.status === 201){
              ElMessage({
                message: '开户成功',
                type: 'success'
              })
            }
          })
          .catch(error => {
            console.log(error)
            ElMessage({
              message: '开户失败：' + error.response.data,
              type: 'error'
            })
          })
    },

    updateCheckingAccount: function () {
      if(!input_fields[3].input_ref){
        ElMessage({
          message: '支票账户号未填写',
          type: 'error'
        })
        return
      }
      let data = {}
      update_indices.forEach(i => data[input_fields[i].name] = input_fields[i].input_ref)
      axios.put(api_url + 'checkingaccount/' + input_fields[3].input_ref + '/', data, auth_config)
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
              message: '更新失败：' + error.response.data,
              type: 'error'
            })
        })
    },

    deleteCheckingAccount: function () {
      axios.delete(api_url + 'checkingaccount/' + input_fields[3].input_ref + '/', auth_config)
        .then(resopnse => {
          if(resopnse.status === 204){
            ElMessage({
              message: '销户成功',
              type: 'success'
            })
          }
        })
        .catch(error => {
          console.log(error)
          ElMessage({
            message: '销户失败：' + error.response.data,
            type: 'error'
          })
        })
    }
  }
}
</script>
