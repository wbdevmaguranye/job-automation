<template>
    <b-container>
      <h1 class="text-success">Bookmarked Jobs</h1>
      <b-table :items="bookmarks" :fields="fields" responsive="sm">
        <!-- Bookmark Details -->
        <template #cell(actions)="data">
          <b-button
            size="sm"
            variant="danger"
            @click="removeBookmark(data.item.bookmark_id)"
          >
            Remove
          </b-button>
        </template>
      </b-table>
    </b-container>
  </template>
  
  <script setup>
  import { onMounted } from "vue";
  import { useBookmarksStore } from "@/stores/bookmarksStore";
  
  const bookmarksStore = useBookmarksStore();
  const userId = 1; // Replace with dynamic user ID
  
  onMounted(() => {
    bookmarksStore.fetchBookmarks(userId);
  });
  
  const bookmarks = computed(() => bookmarksStore.getBookmarks);
  
  const removeBookmark = (bookmarkId) => {
    bookmarksStore.removeBookmark(bookmarkId, userId);
  };
  </script>
  