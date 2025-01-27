// stores/bookmarksStore.js
import { defineStore } from "pinia";
import { useDataStore } from "./dataStore";

export const useBookmarksStore = defineStore("bookmarks", {
  state: () => ({
    bookmarks: [],
  }),
  actions: {
    async fetchBookmarks(userId) {
      const dataStore = useDataStore();
      const response = await dataStore.getData(`/bookmarks/${userId}`);

      if (response.status === "success") {
        this.bookmarks = response.data;
      } else {
        console.error("Error fetching bookmarks:", response.message);
      }
    },

    async addBookmark(userId, jobId) {
      const dataStore = useDataStore();
      const response = await dataStore.postData("/bookmarks", { user_id: userId, job_id: jobId });

      if (response.status === "success") {
        this.fetchBookmarks(userId); // Refresh bookmarks
      } else {
        console.error("Error adding bookmark:", response.message);
      }
    },

    async removeBookmark(bookmarkId, userId) {
      const dataStore = useDataStore();
      const response = await dataStore.deleteData(`/bookmarks/${bookmarkId}`);

      if (response.status === "success") {
        this.fetchBookmarks(userId); // Refresh bookmarks
      } else {
        console.error("Error removing bookmark:", response.message);
      }
    },
  },
  getters: {
    getBookmarks(state) {
      return state.bookmarks;
    },
  },
});
