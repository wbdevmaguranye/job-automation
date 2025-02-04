/// <reference types="vite/client" />

declare module '*.vue' {
    import { DefineComponent } from 'vue';
    const component: DefineComponent<{}, {}, any>;
    export default component;
}

declare module '@/stores/userStore';
declare module '@/middleware/authMiddleware';
declare module '@/components/global/NavBar.vue';
declare module '@/components/Analytics.vue';
declare module '@/components/Applications.vue';
declare module '@/components/CVs.vue';
declare module '@/components/Dashboard.vue';
declare module '@/components/Jobs.vue';
declare module '@/components/Login.vue';
declare module '@/components/Profile.vue';
declare module '@/components/Register.vue';
declare module 'bootstrap-vue-3';

