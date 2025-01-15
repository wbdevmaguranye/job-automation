<template>
  <b-container>
    <!-- Jobs and CVs Stats -->
    <b-row class="mb-4">
      <b-col>
        <b-card title="" class="text-center text-white bg-success">
          <h4>Jobs: {{ jobs.length }}</h4>
        </b-card>
      </b-col>
      <b-col>
        <b-card title="" class="text-center text-white bg-success">
          <h4>Custom CVs: {{ cvs.length }}</h4>
        </b-card>
      </b-col>
    </b-row>

    <!-- Jobs Table -->
    <b-table
      striped
      hover
      bordered
      :items="paginatedJobs"
      :fields="fields"
      responsive="sm"
      class="mb-4 custom-table"
    >
      <!-- Job Link -->
      <template #cell(url)="data">
        <a :href="data.value" target="_blank" class="text-success font-weight-bold">
          View Job
        </a>
      </template>

      <!-- CV Actions -->
      <template #cell(actions)="data">
        <b-button
          size="sm"
          variant="primary"
          @click="viewCV(data.item.id)"
        >
          View CV
        </b-button>
      </template>
    </b-table>

    <!-- CV Modal -->
    <b-modal
      id="cv-modal"
      v-model="showCVModal"
      title="Associated CV"
      size="lg"
    >
      <template v-if="associatedCV">
        <p><strong>CV ID:</strong> {{ associatedCV.id }}</p>
        <p>
          <strong>File URL:</strong>
          <a :href="associatedCV.file_url" target="_blank">{{ associatedCV.file_url }}</a>
        </p>
        <p><strong>Customization Status:</strong> {{ associatedCV.customization_status }}</p>
        <p><strong>Created At:</strong> {{ associatedCV.created_at }}</p>

        <!-- Actions Row -->
        <div class="action-row">
          <!-- Download CV -->
          <b-button size="sm" variant="success" @click="downloadCV">
            Download CV
          </b-button>

          <!-- Replace CV -->
          <div>
            <label for="file-input" class="file-input-label">
              <b-button size="sm" variant="warning">Replace CV</b-button>
            </label>
            <input
              id="file-input"
              type="file"
              class="file-input"
              accept=".docx"
              @change="onFileSelected"
            />
          </div>

          <!-- Apply CV -->
          <b-button
            size="sm"
            variant="primary"
            class="ml-2"
            @click="applyCV(associatedCV.file_url, associatedCV.job_id)"
            :disabled="!associatedCV.file_url"
          >
            Apply CV
          </b-button>
        </div>
      </template>
      <p v-else>No CV available for this job.</p>
    </b-modal>
  </b-container>
</template>

<script setup>
import { ref, computed } from "vue";
import { useJobsStore } from "@/stores/jobsStore";
import { useCVsStore } from "@/stores/cvsStore";

// Table fields for jobs
const fields = [
  { key: "title", label: "Job Title", sortable: true },
  { key: "company", label: "Company", sortable: true },
  { key: "location", label: "Location", sortable: true },
  { key: "url", label: "Link", sortable: false },
  { key: "actions", label: "Actions" },
];

// Collapsed state for job descriptions
const collapsedRows = ref([]);

// Pagination for jobs
const currentJobsPage = ref(1);
const jobsPerPage = 10;

// Search filters
const searchTitle = ref("");
const searchCompany = ref("");
const searchLocation = ref("");

// Data stores
const jobsStore = useJobsStore();
const cvsStore = useCVsStore();
const jobs = ref([]);
const cvs = ref([]);
const associatedCV = ref(null);
const showCVModal = ref(false);
const uploadedFile = ref(null);

// Fetch data on load
const fetchData = async () => {
  await jobsStore.fetchJobs();
  await cvsStore.fetchCVs();
  jobs.value = jobsStore.jobs;
  cvs.value = cvsStore.cvs;

  collapsedRows.value = Array(jobs.value.length).fill(true);
};
fetchData();

// Filtered jobs based on search
const filteredJobs = computed(() =>
  jobs.value.filter(
    (job) =>
      job.title.toLowerCase().includes(searchTitle.value.toLowerCase()) &&
      job.company.toLowerCase().includes(searchCompany.value.toLowerCase()) &&
      job.location?.toLowerCase().includes(searchLocation.value.toLowerCase())
  )
);

// Paginated jobs
const paginatedJobs = computed(() =>
  filteredJobs.value.slice(
    (currentJobsPage.value - 1) * jobsPerPage,
    currentJobsPage.value * jobsPerPage
  )
);

// Toggle description visibility
const toggleDescription = (index) => {
  collapsedRows.value[index] = !collapsedRows.value[index];
};

// View CV
const viewCV = (jobId) => {
  showCVModal.value = true;
  associatedCV.value = cvs.value.find((cv) => cv.job_id === jobId) || null;
};

// Download CV
const downloadCV = () => {
  if (associatedCV.value && associatedCV.value.file_url) {
    const a = document.createElement("a");
    a.href = associatedCV.value.file_url;
    a.download = `CV_${associatedCV.value.id}.docx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  } else {
    alert("File URL not available for this CV.");
  }
};

// Replace CV
const replaceCV = async (cvId) => {
  if (!uploadedFile.value) return alert("Please select a file to upload.");

  const formData = new FormData();
  formData.append("cv", uploadedFile.value);

  try {
    const response = await fetch(`/cvs/${cvId}/upload`, {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      const result = await response.json();
      alert("CV replaced successfully.");
      uploadedFile.value = null;
      associatedCV.value = { ...associatedCV.value, file_url: result.file_url };
      cvsStore.fetchCVs();
    } else {
      alert("Failed to replace CV.");
    }
  } catch (error) {
    console.error("Error replacing CV:", error);
  }
};

// Apply CV
const applyCV = (fileUrl, jobId) => {
  if (!fileUrl) {
    alert("No CV to apply.");
    return;
  }

  const job = jobs.value.find((job) => job.id === jobId);
  if (!job || !job.url) {
    alert("No job URL available.");
    return;
  }

  const confirmation = confirm("Are you sure you want to apply to this job?");
  if (confirmation) {
    window.open(job.url, "_blank");
  }
};

// Handle File Selection
const onFileSelected = (event) => {
  uploadedFile.value = event.target.files[0];
};
</script>

<style scoped>
.action-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-input {
  display: none;
}

.file-input-label {
  cursor: pointer;
}
</style>
