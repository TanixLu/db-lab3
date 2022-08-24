import {createWebHistory, createRouter} from "vue-router";
import ClientManagement from "@/views/ClientManagement";
import SavingAccountManagement from "@/views/SavingAccountManagement";
import CheckingAccountManagement from "@/views/CheckingAccountManagement";
import LoanManagement from "@/views/LoanManagement";
import BusinessStatistics from "@/views/BusinessStatistics";

const routes = [
    {
        path: "/",
        redirect: "/client",
    },
    {
        path: "/client",
        name: "ClientManagement",
        component: ClientManagement
    },
    {
        path: "/saving_account",
        name: "SavingAccountManagement",
        component: SavingAccountManagement
    },
    {
        path: "/checking_account",
        name: "CheckingAccountManagement",
        component: CheckingAccountManagement
    },
    {
        path: "/loan",
        name: "LoanManagement",
        component: LoanManagement
    },
    {
        path: "/statistics",
        name: "BusinessStatistics",
        component: BusinessStatistics
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;
