<template>
  <el-row justify="space-around">

    <el-col :span="14">
      <el-container>
        <el-header height="40px">
          <el-radio-group v-model="radio" size="small" @change="radioChange">
            <el-radio-button label="本月"/>
            <el-radio-button label="本季"/>
            <el-radio-button label="本年"/>
          </el-radio-group>
        </el-header>

        <el-main>
          <el-scrollbar height="450px">
            <el-table :data="statisticsData" border size="small">
              <el-table-column prop="branch_name" label="支行名"/>
              <el-table-column prop="saving_account_num" label="储蓄账户数"/>
              <el-table-column prop="savings" label="储蓄额"/>
              <el-table-column prop="checking_account_num" label="支票账户数"/>
              <el-table-column prop="checking_savings" label="支票储蓄额"/>
              <el-table-column prop="loan_amount" label="贷款发放额"/>
            </el-table>
          </el-scrollbar>
        </el-main>
      </el-container>
    </el-col>

  </el-row>
</template>


<script>
import axios from "axios";

const api_url = 'http://localhost:8000/api/'
const auth_config = {auth: {username: 'tanix', password: '1234'}}

export default {
  name: "BusinessStatistics",
  data() {
    return {
      radio: '本月',
      statisticsData: [
        {
          'branch_name': '',
          'saving_account_num': 0,
          'savings': 0,
          'checking_account_num': 0,
          'checking_savings': 0,
          'loan_amount': 0,
        },
      ],
    }
  },
  mounted() {
    this.radioChange('本月')
  },
  methods: {
    radioChange: function (radio) {
      let vm = this
      axios.post(api_url + 'branch/statistics/', {'radio': radio}, auth_config)
        .then(response => {
          vm.statisticsData = response.data
        })
    },
  }
}
</script>
