<template>
  <el-row justify="space-around">

    <el-col :span="5">
      <el-form
        label-position="left"
        label-width="110px"
        size="small"
      >
        <el-form-item v-for="field in client_loan_fields" :key="field.name" :label="field.zh_name">
          <el-input v-model="field.search_ref"/>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchLoan">查询</el-button>
        </el-form-item>
      </el-form>
    </el-col>

    <el-col :span="8">
      <div class="pagination-block">
        <el-table :data="info.results" border @row-click="fillInput" size="small">
          <el-table-column prop="client_id" label="身份证号"/>
          <el-table-column prop="loan_id" label="贷款号"/>
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
        <el-form-item v-for="field in loan_fields" :key="field.name" :label="field.zh_name">
          <el-input v-model="field.input_ref" :disabled="!(field.name === 'staff_id' && canUpdate)"/>
        </el-form-item>
        <el-form-item>

          <el-dialog
            v-model="releaseDialog"
            :title="'贷款号：' + loan_fields[0].input_ref + '&nbsp;&nbsp;&nbsp;&nbsp;余额：' + loan_fields[3].input_ref"
            width="40%"
          >
            <span>
              <el-scrollbar height="150px">
                <el-row v-for="(client, index) in releaseClients" :key="index">
                  <el-form :inline="true" size="small">
                      <el-form-item :label="'发放人' + (index + 1)" label-width="80px">
                        <el-input v-model="client.id" disabled/>
                      </el-form-item>
                      <el-form-item>
                        <el-input-number v-model="client.amount" :min="0" :max="Number(loan_fields[3].input_ref)"/>
                      </el-form-item>
                      <el-form-item>
                        <el-button type="danger" @click="releaseClients.splice(index, 1)">移除</el-button>
                      </el-form-item>
                  </el-form>
                </el-row>
              </el-scrollbar>
            </span>

            <span>
              <el-scrollbar height="150px">
                <el-table :data="filterReleaseCandidates" border @row-click="addReleaseClient"
                          size="small">
                  <el-table-column prop="id" align="center">
                    <template #header>
                      <el-input v-model="idFilter" size="small" placeholder="输入身份证号过滤"/>
                    </template>
                  </el-table-column>
                </el-table>
              </el-scrollbar>
            </span>

            <template #footer>
              <span class="dialog-footer">
                <el-button @click="releaseDialog = false">取消</el-button>
                <el-button @click="releaseLoan" type="primary">发放</el-button>
              </span>
            </template>
          </el-dialog>

          <el-dialog
            v-model="newLoanDialog"
            title="新建贷款"
            width="40%"
          >
            <span>
              <el-form size="small">
                <el-row>
                  <el-col :span="8">
                    <el-form-item label="总额">
                      <el-input-number v-model="newLoanTotal" :min="0"/>
                    </el-form-item>
                  </el-col>
                  <el-col :span="13">
                    <el-form-item label="支行名">
                      <el-input v-model="newLoanBranchName"/>
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-row>
                  <el-col :span="16">
                    <el-form-item label="负责人身份证号" label-width="110px">
                      <el-input v-model="newLoanStaffId"/>
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="&nbsp;&nbsp;">
                      <el-button type="success" @click="newLoanClients.push({'id': ''})">添加发放人</el-button>
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-divider/>

                <el-scrollbar height="240px">
                  <el-row v-for="(client, index) in newLoanClients" :key="index">
                    <el-form-item :label="'发放人' + (index + 1)" label-width="80px">
                      <el-input v-model="client.id"/>
                    </el-form-item>
                    <el-form-item label-width="20px">
                      <el-button type="danger" @click="newLoanClients.splice(index, 1)" size="small">
                        移除</el-button>
                    </el-form-item>
                  </el-row>
                </el-scrollbar>
              </el-form>
            </span>
            
            <template #footer>
              <span class="dialog-footer">
                <el-button @click="newLoanDialog = false">取消</el-button>
                <el-button @click="createLoan" type="success">新建</el-button>
              </span>
            </template>
          </el-dialog>

          <el-button type="warning" @click="updateLoan" v-if="canUpdate">更新</el-button>
          <el-button type="primary" @click="openReleaseDialog" v-if="loan_fields[3].input_ref > 0">发放</el-button>
          <el-button type="danger" @click="deleteLoan" v-if="
              loan_fields[2].input_ref && loan_fields[3].input_ref &&
              (parseFloat(loan_fields[3].input_ref) === 0.0 ||
                parseFloat(loan_fields[2].input_ref) === parseFloat(loan_fields[3].input_ref))
            ">删除</el-button>
          <el-button type="success" @click="newLoanDialog = true">新建贷款</el-button>
        </el-form-item>
      </el-form>
    </el-col>

  </el-row>
</template>


<script>
import axios from "axios";
import {ElMessage} from "element-plus";

const client_loan_fields = [
  {'name': 'client_id', 'zh_name': '身份证号'},
  {'name': 'loan_id', 'zh_name': '贷款号'},
]
client_loan_fields.forEach(field => field['search_ref'] = '')

const loan_fields = [
  {'name': 'id', 'zh_name': '贷款号'},
  {'name': 'branch_name', 'zh_name': '支行名'},
  {'name': 'total', 'zh_name': '总额'},
  {'name': 'balance', 'zh_name': '余额'},
  {'name': 'staff_id', 'zh_name': '负责人身份证号'},
]
loan_fields.forEach(field => field['input_ref'] = '')

const api_url = 'http://localhost:8000/api/'
const auth_config = {auth: {username: 'tanix', password: '1234'}}

export default {
  name: "LoanManagement",
  data() {
    return {
      client_loan_fields,
      loan_fields,
      currentPage: 1,
      pageCount: 0,
      query_url: api_url + 'client_loan/?',
      info: '',
      canUpdate: false,
      releaseDialog: false,
      newLoanDialog: false,
      releaseClients: [{'id': '', 'amount': 0},],
      idFilter: '',
      releaseCandidates: [{'id': ''},],
      newLoanTotal: 0,
      newLoanBranchName: '',
      newLoanStaffId: '',
      newLoanClients: [{'id': ''},],
    }
  },
  computed: {
    filterReleaseCandidates() {
      let vm = this
      return vm.releaseCandidates.filter(
          candidate => !vm.idFilter || candidate.id.toUpperCase().includes(vm.idFilter.toUpperCase())
      )
    }
  },
  mounted() {
    this.searchLoan()
  },
  watch: {
    currentPage: async function(newPage) {
      this.info = (await axios.get(this.query_url + 'page=' + newPage.toString(), auth_config)).data
      this.pageCount = Math.ceil(this.info.count / 8)
    }
  },
  methods: {
    searchLoan: async function () {
      let vm = this
      vm.currentPage = 1
      vm.query_url = api_url + 'client_loan/?'
      client_loan_fields.forEach(field => {
        if(field.search_ref)
          vm.query_url += field.name + '=' + field.search_ref + '&'
      })
      vm.info = (await axios.get(vm.query_url, auth_config)).data
      this.pageCount = Math.ceil(this.info.count / 8)
    },

    fillInput: function (client_loan) {
      let vm = this
      axios.get(api_url + 'loan/' + client_loan['loan_id'] + '/', auth_config)
        .then(response => {
          vm.loan_fields[0].input_ref = response.data['id']
          vm.loan_fields[1].input_ref = response.data['branch_name']
          vm.loan_fields[2].input_ref = response.data['total']
          vm.loan_fields[3].input_ref = response.data['balance']
          vm.loan_fields[4].input_ref = response.data['staff_id']
          vm.canUpdate = response.data['staff_id'] === null;
        })
    },

    updateLoan: function () {
      let vm = this
      let data = {
        'loan_id': loan_fields[0].input_ref,
        'staff_id': loan_fields[4].input_ref
      }
      axios.put(api_url + 'loan/' + loan_fields[0].input_ref + '/', data, auth_config)
        .then(response => {
          if(response.status === 200){
            vm.canUpdate = false
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

    releaseLoan: function () {
      let vm = this
      let data = {
        'loan_id': vm.loan_fields[0].input_ref,
        'clients': vm.releaseClients,
      }
      axios.post(api_url + 'loan/release_loan/', data, auth_config)
        .then(response => {
          if(response.status === 200){
            let client_loan = {'loan_id': vm.loan_fields[0].input_ref}
            vm.fillInput(client_loan)
            ElMessage({
              message: '发放成功',
              type: 'success'
            })
          }
        })
        .catch(error => {
          console.log(error)
          ElMessage({
            message: '发放失败：' + error.response.data,
            type: 'error'
          })
        })
    },

    deleteLoan: function () {
      let vm = this
      axios.delete(api_url + 'loan/' + vm.loan_fields[0].input_ref + '/', auth_config)
        .then(resopnse => {
          if(resopnse.status === 204){
            ElMessage({
              message: '删除成功',
              type: 'success'
            })
          }
        })
        .catch(error => {
          console.log(error)
          ElMessage({
            message: '删除失败：' + error.response.data,
            type: 'error'
          })
        })
    },

    addReleaseClient: function (candidate) {
      let vm = this
      for(let i = 0; i < vm.releaseClients.length; i++){
        if(vm.releaseClients[i].id === candidate.id)
          return
      }
      vm.releaseClients.push({
        'id': candidate.id,
        'amount': 0,
      })
    },

    openReleaseDialog: async function () {
      let vm = this
      vm.releaseDialog = true
      vm.releaseClients = []
      vm.releaseCandidates = []
      let url = api_url + 'client_loan/?loan_id=' + vm.loan_fields[0].input_ref
      do{
        let response = await axios.get(url, auth_config)
        url = response.data.next
        response.data.results.forEach(client_loan => {
          vm.releaseCandidates.push({'id': client_loan['client_id']})
        })
      }while(url)
    },

    createLoan: function () {
      let vm = this
      let data = {
        'total': vm.newLoanTotal,
        'branch_name': vm.newLoanBranchName,
        'staff_id': vm.newLoanStaffId,
        'clients': vm.newLoanClients
      }
      axios.post(api_url + 'loan/create_loan/', data, auth_config)
          .then(response => {
            if(response.status === 201){
              ElMessage({
                message: '新建成功',
                type: 'success'
              })
            }
          })
          .catch(error => {
            console.log(error)
            ElMessage({
              message: '新建失败：' + error.response.data,
              type: 'error'
            })
          })
    }
  }
}
</script>
