<template>
  <div class="fixed inset-0 flex flex-col overflow-hidden">
    <AppMenuBar class="relative z-40 m-0! p-0! rounded-none! border-none!" />

    <div class="flex-1 min-h-0 overflow-hidden">
      <div class="content h-full min-h-0 bg-[#121116]">
        <div class="h-full min-h-0 w-full">
          <div class="relative h-full min-h-0 w-full">
            <Dialog
              v-model:visible="showSidebar"
              header="Enter Birth Data"
              modal
              :pt="birthDataDialogPt"
              :ptOptions="{ mergeProps: true }"
            >
              <form @submit.prevent="generateChart" class="@container flex flex-1 flex-col">
                <div class="flex-1 space-y-4">
                  <div class="min-w-0">
                    <label class="astro-field-caption">Name</label>
                    <InputText
                      v-model="formData.name"
                      class="w-full"
                      fluid
                      placeholder="Name"
                      size="small"
                      :pt="inputTextPt"
                      :ptOptions="{ mergeProps: true }"
                    />
                  </div>
                  <p
                    class="m-0 border-b border-[#4a454e] pb-1 text-xs font-semibold tracking-[0.1em] text-[#c9a467] uppercase"
                  >
                    Date of Birth
                  </p>
                  <div class="grid grid-cols-1 gap-2 @xs:grid-cols-3">
                    <div class="min-w-0">
                      <label class="astro-field-caption">Day</label>
                      <InputNumber
                        v-model="formData.day"
                        :min="1"
                        :max="31"
                        fluid
                        placeholder="Day"
                        size="small"
                        :pt="inputNumberPt"
                        :ptOptions="{ mergeProps: true }"
                      />
                    </div>
                    <div class="min-w-0">
                      <label class="astro-field-caption">Month</label>
                      <InputNumber
                        v-model="formData.month"
                        :min="1"
                        :max="12"
                        fluid
                        placeholder="Month"
                        size="small"
                        :pt="inputNumberPt"
                        :ptOptions="{ mergeProps: true }"
                      />
                    </div>
                    <div class="min-w-0">
                      <label class="astro-field-caption">Year</label>
                      <InputNumber
                        v-model="formData.year"
                        :format="false"
                        :min="-3500"
                        fluid
                        placeholder="Year"
                        size="small"
                        :pt="inputNumberPt"
                        :ptOptions="{ mergeProps: true }"
                      />
                    </div>
                  </div>
                  <p
                    class="m-0 border-b border-[#4a454e] pb-1 text-xs font-semibold tracking-[0.1em] text-[#c9a467] uppercase"
                  >
                    Birth Information
                  </p>
                  <div class="grid grid-cols-1 gap-2 @sm:grid-cols-2">
                    <div class="min-w-0">
                      <label class="astro-field-caption">Hour</label>
                      <InputNumber
                        v-model="formData.hour"
                        :min="0"
                        :max="23"
                        fluid
                        placeholder="Hour"
                        size="small"
                        :pt="inputNumberPt"
                        :ptOptions="{ mergeProps: true }"
                      />
                    </div>

                    <div class="min-w-0">
                      <label class="astro-field-caption">Minute</label>
                      <InputNumber
                        v-model="formData.minute"
                        :min="0"
                        :max="59"
                        fluid
                        placeholder="Minute"
                        size="small"
                        :pt="inputNumberPt"
                        :ptOptions="{ mergeProps: true }"
                      />
                    </div>
                  </div>
                  <p
                    class="m-0 border-b border-[#4a454e] pb-1 text-xs font-semibold tracking-[0.1em] text-[#c9a467] uppercase"
                  >
                    Location Information
                  </p>
                  <div class="grid grid-cols-1 gap-2 @sm:grid-cols-2">
                    <div class="min-w-0">
                      <label class="astro-field-caption">Latitude</label>
                      <InputNumber
                        v-model="formData.lat"
                        :format="false"
                        :maxFractionDigits="6"
                        :min="-90"
                        :max="90"
                        fluid
                        placeholder="Latitude"
                        size="small"
                        :pt="inputNumberPt"
                        :ptOptions="{ mergeProps: true }"
                      />
                    </div>

                    <div class="min-w-0">
                      <label class="astro-field-caption">Longitude</label>
                      <InputNumber
                        v-model="formData.lng"
                        :format="false"
                        :maxFractionDigits="6"
                        :min="-180"
                        :max="180"
                        fluid
                        placeholder="Longitude"
                        size="small"
                        :pt="inputNumberPt"
                        :ptOptions="{ mergeProps: true }"
                      />
                    </div>

                    <div class="min-w-0 @sm:col-span-2">
                      <label class="astro-field-caption">Timezone</label>
                      <InputText
                        v-model="formData.tz_str"
                        class="astro-timezone w-full"
                        fluid
                        placeholder="Resolved from coordinates"
                        size="small"
                        :pt="inputTextPt"
                        :ptOptions="{ mergeProps: true }"
                        @update:model-value="onTimezoneInput"
                      />
                    </div>

                    <div class="min-w-0">
                      <label class="astro-field-caption">City</label>
                      <InputText
                        v-model="formData.city"
                        class="w-full"
                        fluid
                        placeholder="City"
                        size="small"
                        :pt="inputTextPt"
                        :ptOptions="{ mergeProps: true }"
                      />
                    </div>
                    <div class="min-w-0">
                      <label class="astro-field-caption">Country</label>
                      <InputText
                        v-model="formData.nation"
                        class="w-full"
                        fluid
                        placeholder="Country"
                        size="small"
                        :pt="inputTextPt"
                        :ptOptions="{ mergeProps: true }"
                      />
                    </div>
                  </div>
                  <p
                    class="m-0 border-b border-[#4a454e] pb-1 text-xs font-semibold tracking-[0.1em] text-[#c9a467] uppercase"
                  >
                    House System
                  </p>
                  <div class="min-w-0">
                    <Select
                      v-model="formData.houses_system"
                      :options="houseSystemOptions"
                      optionLabel="label"
                      optionValue="code"
                      class="astro-house-system w-full"
                      size="small"
                      placeholder="House System"
                      :pt="selectPt"
                      :ptOptions="{ mergeProps: true }"
                    />
                  </div>

                  <div class="mt-4 flex gap-2 border-t border-[#4a454e] pt-3">
                    <Button
                      type="submit"
                      label="Generate Chart"
                      :loading="loading"
                      class="w-full"
                      icon="pi pi-chart-line"
                      :pt="primaryButtonPt"
                      :ptOptions="{ mergeProps: true }"
                    />
                    <Button
                      type="button"
                      label="Reset"
                      severity="secondary"
                      outlined
                      class="w-full"
                      icon="pi pi-refresh"
                      @click="resetForm"
                      :disabled="loading"
                      :pt="secondaryButtonPt"
                      :ptOptions="{ mergeProps: true }"
                    />
                  </div>
                </div>
              </form>
              <!-- Loading overlay while ephemeris / chart is in progress -->
              <!-- Progress bar when the drawer is open -->
              <div
                v-if="loading && showSidebar"
                class="mt-4 space-y-2 border-t border-[#4a454e] pt-3"
              >
                <p class="text-sm font-medium text-[#f2eee5]">
                  {{
                    loadingStage === 'ephemeris'
                      ? 'Downloading ephemeris data…'
                      : 'Generating birth chart…'
                  }}
                </p>
                <ProgressBar mode="indeterminate" :pt="progressBarPt" style="height: 6px" />
                <p v-if="loadingStage === 'ephemeris'" class="text-xs text-[#aaa39a]">
                  First use for this century downloads a small data file. It is stored locally for
                  later charts.
                </p>
              </div>
            </Dialog>

            <!-- Chart Display -->
            <div class="chart-stage relative z-0 h-full min-h-0 min-w-0 w-full overflow-hidden">
              <div class="chart-shell">
                <div
                  :class="[
                    'chart-shell__main',
                    svgUrl ? 'chart-shell__main--chart' : 'chart-shell__main--empty',
                  ]"
                >
                  <template v-if="svgUrl">
                    <div class="chart-shell__toolbar">
                      <div class="chart-shell__toolbar-primary">
                        <Button
                          label="Edit Birth Data"
                          icon="pi pi-bars"
                          class="chart-shell__birth-data"
                          :pt="primaryButtonPt"
                          :ptOptions="{ mergeProps: true }"
                          @click="showSidebar = true"
                        />
                      </div>
                      <div class="chart-shell__toolbar-secondary">
                        <Button
                          label="View Full Screen"
                          icon="pi pi-external-link"
                          @click="showFullScreen = true"
                          outlined
                          :pt="outlinedPrimaryButtonPt"
                          :ptOptions="{ mergeProps: true }"
                        />
                        <Button
                          :label="showMagnifier ? 'Hide Magnifier' : 'Show Magnifier'"
                          icon="pi pi-search-plus"
                          @click="toggleMagnifier"
                          outlined
                          :pt="outlinedPrimaryButtonPt"
                          :ptOptions="{ mergeProps: true }"
                        />
                      </div>
                    </div>

                    <div class="chart-shell__viewport">
                      <div class="chart-shell__chart-frame">
                        <img
                          :src="svgUrl"
                          :key="svgUrl"
                          alt="Birth Chart"
                          class="block h-auto w-auto max-h-full max-w-full object-contain"
                        />
                        <div
                          v-if="showMagnifier"
                          class="absolute inset-0 z-10 overflow-hidden border border-[#c9a467] bg-[#17191a] shadow-lg"
                        >
                          <div class="h-full w-full overflow-auto">
                            <img
                              :src="svgUrl"
                              alt="Magnified Birth Chart"
                              class="block max-w-none"
                              :style="{
                                width: `${magnifierScale * 100}%`,
                                height: 'auto',
                              }"
                            />
                          </div>
                        </div>
                      </div>
                    </div>

                    <div
                      v-if="preferencesOptions.aspects.length"
                      class="chart-shell__dock chart-aspects-panel"
                    >
                      <div class="chart-shell__dock-header">
                        <p class="m-0 text-sm font-semibold">Visible aspects</p>
                        <div class="chart-aspects-actions flex items-center gap-2">
                          <Button
                            label="All"
                            text
                            size="small"
                            class="astro-aspect-preset"
                            :aria-pressed="isAspectPresetActive(preferences.aspects_enabled, 'all')"
                            :disabled="savingPreferences || loadingPreferences || loading"
                            @click="applyChartAspectPreset('all')"
                            :pt="textButtonPt"
                            :ptOptions="{ mergeProps: true }"
                          />
                          <Button
                            label="Major"
                            text
                            size="small"
                            class="astro-aspect-preset"
                            :aria-pressed="isAspectPresetActive(preferences.aspects_enabled, 'major')"
                            :disabled="savingPreferences || loadingPreferences || loading"
                            @click="applyChartAspectPreset('major')"
                            :pt="textButtonPt"
                            :ptOptions="{ mergeProps: true }"
                          />
                          <Button
                            label="None"
                            text
                            size="small"
                            class="astro-aspect-preset"
                            :aria-pressed="isAspectPresetActive(preferences.aspects_enabled, 'none')"
                            :disabled="savingPreferences || loadingPreferences || loading"
                            @click="applyChartAspectPreset('none')"
                            :pt="textButtonPt"
                            :ptOptions="{ mergeProps: true }"
                          />
                        </div>
                      </div>
                      <div class="chart-shell__aspect-list">
                        <button
                          v-for="aspect in preferencesOptions.aspects"
                          :key="`chart-aspect-${aspect.key}`"
                          type="button"
                          :class="[
                            'astro-aspect-option',
                          ]"
                          :aria-pressed="!!preferences.aspects_enabled[aspect.key]"
                          :disabled="savingPreferences || loadingPreferences || loading"
                          @click="
                            updateAspectPreference(
                              aspect.key,
                              !preferences.aspects_enabled[aspect.key],
                            )
                          "
                        >
                          <span class="text-sm font-medium">{{ aspect.label }}</span>
                          <span
                            class="rounded-none bg-[#302b2b] px-2 py-0.5 text-xs whitespace-nowrap text-[#c9a467]"
                            >orb {{ aspect.default_orb }}</span
                          >
                        </button>
                      </div>
                    </div>
                  </template>

                  <div
                    v-else
                    class="chart-shell__empty flex h-full min-h-0 flex-col items-center justify-center text-center text-[#aaa39a]"
                  >
                    <div
                      class="relative mb-5 flex h-44 w-44 items-center justify-center"
                      aria-hidden="true"
                    >
                      <div class="chart-empty-orbit"></div>
                      <div class="chart-empty-axis"></div>
                    </div>
                    <p
                      class="mb-2 text-[0.68rem] font-semibold tracking-[0.16em] text-[#c9a467] uppercase"
                    >
                      Natal chart workspace
                    </p>
                    <p class="max-w-md text-[0.94rem] leading-normal text-[#aaa39a]">
                      Open Birth Data, enter birth time and location, then generate your chart.
                    </p>
                    <Button
                      label="Open Birth Data"
                      icon="pi pi-arrow-right"
                      iconPos="right"
                      class="mt-6 rounded-none border border-[#c9a467] bg-[#c9a467] px-4 text-[#121116] hover:border-[#e0be7b] hover:bg-[#e0be7b]"
                      :pt="primaryButtonPt"
                      :ptOptions="{ mergeProps: true }"
                      @click="showSidebar = true"
                    />
                  </div>
                </div>
              </div>
              <!-- Progress overlay when the drawer is closed -->
              <div
                v-if="loading && !showSidebar"
                class="absolute inset-0 z-20 flex flex-col items-center justify-center gap-4 bg-[#121116]/95 p-6"
              >
                <p class="text-sm font-medium text-[#f2eee5]">
                  {{
                    loadingStage === 'ephemeris'
                      ? 'Downloading ephemeris data…'
                      : 'Generating birth chart…'
                  }}
                </p>
                <ProgressBar
                  mode="indeterminate"
                  class="w-full max-w-xs"
                  :pt="progressBarPt"
                  style="height: 6px"
                />
                <p
                  v-if="loadingStage === 'ephemeris'"
                  class="max-w-xs text-center text-xs text-[#aaa39a]"
                >
                  First use for this century downloads a small data file. It is stored locally for
                  later charts.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div
          v-if="showFullScreen && svgUrl"
          class="astro-chart-fullscreen fixed inset-0 z-50 flex items-center justify-center bg-[#17191a] p-4"
        >
          <div class="absolute right-4 top-4 z-10 flex items-center gap-2">
            <Button
              v-if="hasFullscreenDetails && !showFullscreenDetailsPanel"
              label="Details"
              outlined
              @click="showFullscreenDetailsPanel = true"
              aria-label="Show chart details"
              :pt="outlinedPrimaryButtonPt"
              :ptOptions="{ mergeProps: true }"
            />
            <Button
              icon="pi pi-times"
              outlined
              @click="showFullScreen = false"
              aria-label="Close full screen chart"
              :pt="outlinedPrimaryButtonPt"
              :ptOptions="{ mergeProps: true }"
            />
          </div>
          <div class="astro-chart-fullscreen-stage">
            <div
              v-if="fullscreenSvg"
              class="astro-chart-fullscreen-wheel"
              aria-label="Birth Chart Full Screen"
              v-html="fullscreenSvg"
            />
            <img
              v-else
              :src="svgUrl"
              :key="svgUrl"
              alt="Birth Chart Full Screen"
              class="max-h-full max-w-full object-contain"
            />
            <aside
              v-if="hasFullscreenDetails && showFullscreenDetailsPanel"
              class="astro-chart-fullscreen-details"
            >
              <div class="astro-chart-fullscreen-details-header">
                <h2>{{ chartData?.name || 'Natal chart' }}</h2>
                <button
                  type="button"
                  class="astro-chart-fullscreen-details-close"
                  aria-label="Hide chart details"
                  @click="showFullscreenDetailsPanel = false"
                >
                  <i class="pi pi-times" aria-hidden="true" />
                </button>
              </div>
              <dl>
                <div v-if="chartData?.date">
                  <dt>Date</dt>
                  <dd>{{ chartData.date }}</dd>
                </div>
                <div v-if="fullscreenLocation">
                  <dt>Location</dt>
                  <dd>{{ fullscreenLocation }}</dd>
                </div>
                <div v-if="chartData?.zodiac_type">
                  <dt>Zodiac</dt>
                  <dd>{{ chartData.zodiac_type }}</dd>
                </div>
                <div v-if="chartData?.houses_system">
                  <dt>Houses</dt>
                  <dd>{{ chartData.houses_system }}</dd>
                </div>
                <div v-if="fullscreenAscendant">
                  <dt>Ascendant</dt>
                  <dd>{{ fullscreenAscendant }}</dd>
                </div>
                <div v-if="fullscreenMidheaven">
                  <dt>Midheaven</dt>
                  <dd>{{ fullscreenMidheaven }}</dd>
                </div>
              </dl>
              <section v-if="fullscreenPlanetRows.length" class="astro-disclosure">
                <button
                  type="button"
                  class="astro-disclosure-toggle"
                  :aria-expanded="fullscreenOpenSections.planets"
                  @click="toggleFullscreenSection('planets')"
                >
                  <span>Planets</span>
                  <i
                    :class="
                      fullscreenOpenSections.planets ? 'pi pi-chevron-down' : 'pi pi-chevron-right'
                    "
                    aria-hidden="true"
                  />
                </button>
                <ul v-show="fullscreenOpenSections.planets" class="m-0 list-none p-0">
                  <li v-for="planet in fullscreenPlanetRows" :key="planet.name">
                    <span>{{ planet.name }}</span>
                    <span>{{ planet.detail }}</span>
                  </li>
                </ul>
              </section>
              <section v-if="fullscreenHouseRows.length" class="astro-disclosure">
                <button
                  type="button"
                  class="astro-disclosure-toggle"
                  :aria-expanded="fullscreenOpenSections.cusps"
                  @click="toggleFullscreenSection('cusps')"
                >
                  <span>Cusps</span>
                  <i
                    :class="
                      fullscreenOpenSections.cusps ? 'pi pi-chevron-down' : 'pi pi-chevron-right'
                    "
                    aria-hidden="true"
                  />
                </button>
                <ul v-show="fullscreenOpenSections.cusps" class="m-0 list-none p-0">
                  <li v-for="house in fullscreenHouseRows" :key="house.name">
                    <span>{{ house.name }}</span>
                    <span>{{ house.detail }}</span>
                  </li>
                </ul>
              </section>
              <section v-if="fullscreenAspectRows.length" class="astro-disclosure">
                <button
                  type="button"
                  class="astro-disclosure-toggle"
                  :aria-expanded="fullscreenOpenSections.aspects"
                  @click="toggleFullscreenSection('aspects')"
                >
                  <span>Aspects</span>
                  <i
                    :class="
                      fullscreenOpenSections.aspects ? 'pi pi-chevron-down' : 'pi pi-chevron-right'
                    "
                    aria-hidden="true"
                  />
                </button>
                <ul v-show="fullscreenOpenSections.aspects" class="m-0 list-none p-0">
                  <li v-for="aspect in fullscreenAspectRows" :key="aspect.key">
                    <span>{{ aspect.text }}</span>
                    <span v-if="aspect.orb">{{ aspect.orb }}</span>
                  </li>
                </ul>
              </section>
            </aside>
          </div>
        </div>
        <img
          v-if="printSvgUrl"
          :src="printSvgUrl"
          class="print-chart-image"
          alt=""
          aria-hidden="true"
        />

        <Dialog
          v-model:visible="showPreferencesDialog"
          modal
          header="Edit Preferences"
          :pt="preferencesDialogPt"
          :ptOptions="{ mergeProps: true }"
        >
          <p class="m-0 mb-4 text-sm text-[#aaa39a]">
            Configure zodiac, house system, and enabled aspects.
          </p>
          <div class="space-y-4" v-if="preferencesDraft">
            <div>
              <label
                class="mb-1 block text-xs font-semibold tracking-[0.08em] text-[#c9a467] uppercase"
                >Zodiac Type</label
              >
              <Select
                v-model="preferencesDraft.zodiac_type"
                :options="preferencesOptions.zodiac_types"
                class="w-full"
                size="small"
                :pt="selectPt"
                :ptOptions="{ mergeProps: true }"
                :disabled="savingPreferences || loadingPreferences"
              />
            </div>

            <div>
              <label
                class="mb-1 block text-xs font-semibold tracking-[0.08em] text-[#c9a467] uppercase"
                >House System</label
              >
              <Select
                v-model="preferencesDraft.houses_system"
                :options="preferencesOptions.house_systems"
                optionLabel="label"
                optionValue="code"
                class="w-full"
                size="small"
                :pt="selectPt"
                :ptOptions="{ mergeProps: true }"
                :disabled="savingPreferences || loadingPreferences"
              />
            </div>

            <div>
              <div
                class="mb-2 flex flex-wrap items-center justify-between gap-2 border-b border-[#4a454e] pb-1"
              >
                <label
                  class="m-0 block text-xs font-semibold tracking-[0.08em] text-[#c9a467] uppercase"
                  >Enabled Aspects</label
                >
                <div class="chart-aspects-actions flex items-center gap-2">
                  <Button
                    label="All"
                    text
                    size="small"
                    class="astro-aspect-preset"
                    :aria-pressed="isAspectPresetActive(preferencesDraft.aspects_enabled, 'all')"
                    :pt="textButtonPt"
                    :ptOptions="{ mergeProps: true }"
                    :disabled="savingPreferences || loadingPreferences"
                    @click="applyDraftAspectPreset('all')"
                  />
                  <Button
                    label="Major"
                    text
                    size="small"
                    class="astro-aspect-preset"
                    :aria-pressed="isAspectPresetActive(preferencesDraft.aspects_enabled, 'major')"
                    :pt="textButtonPt"
                    :ptOptions="{ mergeProps: true }"
                    :disabled="savingPreferences || loadingPreferences"
                    @click="applyDraftAspectPreset('major')"
                  />
                  <Button
                    label="None"
                    text
                    size="small"
                    class="astro-aspect-preset"
                    :aria-pressed="isAspectPresetActive(preferencesDraft.aspects_enabled, 'none')"
                    :pt="textButtonPt"
                    :ptOptions="{ mergeProps: true }"
                    :disabled="savingPreferences || loadingPreferences"
                    @click="applyDraftAspectPreset('none')"
                  />
                </div>
              </div>
              <div
                class="grid max-h-[min(30vh,13rem)] grid-cols-1 gap-1.5 overflow-y-auto pr-0.5 sm:grid-cols-2"
              >
                <button
                  v-for="aspect in preferencesOptions.aspects"
                  :key="aspect.key"
                  type="button"
                  :class="[
                    'astro-aspect-option',
                  ]"
                  :aria-pressed="!!preferencesDraft.aspects_enabled[aspect.key]"
                  :disabled="savingPreferences || loadingPreferences"
                  @click="
                    preferencesDraft.aspects_enabled[aspect.key] =
                      !preferencesDraft.aspects_enabled[aspect.key]
                  "
                >
                  <span class="text-sm font-medium">{{ aspect.label }}</span>
                  <span
                    class="rounded-none bg-[#302b2b] px-2 py-0.5 text-xs whitespace-nowrap text-[#c9a467]"
                    >orb {{ aspect.default_orb }}</span
                  >
                </button>
              </div>
            </div>
          </div>
          <template #footer>
            <div class="flex items-center justify-end gap-2 border-t border-[#4a454e] pt-3">
              <Button
                label="Cancel"
                severity="secondary"
                outlined
                @click="cancelPreferences"
                :disabled="savingPreferences"
                :pt="secondaryButtonPt"
                :ptOptions="{ mergeProps: true }"
              />
              <Button
                label="Save Preferences"
                icon="pi pi-save"
                @click="savePreferences"
                :loading="savingPreferences"
                :pt="primaryButtonPt"
                :ptOptions="{ mergeProps: true }"
              />
            </div>
          </template>
        </Dialog>

        <Dialog
          v-model:visible="showAboutDialog"
          modal
          header="About Simple Astro Chart"
          :pt="aboutDialogPt"
          :ptOptions="{ mergeProps: true }"
        >
          <p class="m-0 mb-3 text-sm text-[#f4eee4]">A standalone offline natal chart app.</p>
          <dl class="m-0 space-y-2 text-sm text-[#bdb4a7]">
            <div>
              <dt class="text-[0.62rem] font-semibold tracking-[0.1em] text-[#c9a467] uppercase">
                Built with
              </dt>
              <dd class="m-0">Vue, PrimeVue, Kerykeion, FastAPI, and Electron</dd>
            </div>
            <div>
              <dt class="text-[0.62rem] font-semibold tracking-[0.1em] text-[#c9a467] uppercase">
                Ephemeris
              </dt>
              <dd class="m-0">Swiss Ephemeris, downloaded on demand and stored locally</dd>
            </div>
          </dl>
        </Dialog>
      </div>
    </div>
  </div>
</template>

<script setup>
import AppMenuBar from './components/AppMenuBar.vue'
import { ref, computed, onMounted, onBeforeUnmount, provide, watch, nextTick } from 'vue'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import Select from 'primevue/select'
import ProgressBar from 'primevue/progressbar'
import { useStatusMessage } from './composables/useStatusMessage.js'
import { joinList, toUserErrorMessage } from './lib/apiError.js'

const buttonPt = {
  root: {
    class: 'astro-control astro-button',
  },
  label: { class: 'astro-button-label leading-none' },
  icon: { class: 'astro-button-icon' },
}

const primaryButtonPt = {
  ...buttonPt,
  root: {
    class:
      'astro-control astro-button astro-button-primary border border-[#c9a467] bg-[#c9a467] text-[#17191a] hover:border-[#e0be7b] hover:bg-[#e0be7b]',
    style: {
      borderColor: '#c9a467',
      backgroundColor: '#c9a467',
      color: '#17191a',
    },
  },
}

const secondaryButtonPt = {
  ...buttonPt,
  root: {
    class:
      'astro-control astro-button astro-button-secondary border border-[#5c625e] bg-transparent text-[#bdb4a7] hover:border-[#c9a467] hover:bg-[#2b302d] hover:text-[#f4eee4]',
    style: {
      borderColor: '#5c625e',
      backgroundColor: 'transparent',
      color: '#bdb4a7',
    },
  },
}

const outlinedPrimaryButtonPt = {
  ...buttonPt,
  root: {
    class:
      'astro-control astro-button astro-button-outlined-primary border border-[#c9a467] bg-transparent text-[#c9a467] hover:border-[#e0be7b] hover:bg-[#2b302d] hover:text-[#e0be7b]',
    style: {
      borderColor: '#c9a467',
      backgroundColor: 'transparent',
      color: '#c9a467',
    },
  },
}

const textButtonPt = {
  ...buttonPt,
  root: {
    class:
      'astro-control astro-button astro-button-text border border-transparent bg-transparent text-[#c9a467] hover:border-[#5c625e] hover:bg-[#2b302d] hover:text-[#f4eee4]',
    style: {
      backgroundColor: 'transparent',
      color: '#c9a467',
    },
  },
}

const inputTextPt = {
  root: {
    class:
      'astro-control astro-input h-[34px] rounded-[2px] border border-[#5c625e] bg-[#17191a] px-2.5 py-1.5 text-sm text-[#f4eee4] shadow-none placeholder:text-[#8d8b82]',
    style: {
      height: '34px',
      borderRadius: '2px',
      borderColor: '#5c625e',
      backgroundColor: '#17191a',
      color: '#f4eee4',
    },
  },
}

const inputNumberPt = {
  root: {
    class: 'astro-number w-full min-w-0',
    style: {
      display: 'block',
      width: '100%',
      minHeight: '34px',
    },
  },
}

const selectPt = {
  root: {
    class:
      'astro-control astro-select flex h-[34px] w-full items-center rounded-[2px] border border-[#5c625e] bg-[#17191a] text-sm text-[#f4eee4] shadow-none',
    style: {
      height: '34px',
      borderRadius: '2px',
      borderColor: '#5c625e',
      backgroundColor: '#17191a',
      color: '#f4eee4',
    },
  },
  label: { class: 'min-w-0 flex-1 px-2.5 py-1.5 text-sm text-[#f4eee4]' },
  dropdown: { class: 'ml-auto flex h-full w-8 shrink-0 items-center justify-center text-[#c9a467]' },
  dropdownIcon: { class: 'text-[#c9a467]' },
  overlay: {
    class: 'astro-select-overlay max-w-full overflow-hidden rounded-[2px] border border-[#5c625e] bg-[#222625] shadow-xl',
  },
  listContainer: { class: 'max-h-[min(40vh,16rem)] overflow-y-auto' },
  list: { class: 'p-1' },
  option: {
    class:
      'rounded-[2px] px-2 py-1.5 text-sm text-[#bdb4a7] hover:bg-[#2b302d] hover:text-[#f4eee4]',
  },
}

const birthDataDialogPt = {
  mask: {
    class: 'astro-dialog-mask',
  },
  root: {
    class:
      'astro-dialog astro-birth-data-dialog w-[min(92vw,34rem)] rounded-[2px] border border-[#5c625e] bg-[#222625] shadow-2xl',
  },
  header: {
    class: 'astro-overlay-header border-b border-[#5c625e] bg-[#17191a] px-4 py-3 text-[#f4eee4]',
  },
  title: { class: 'text-sm font-semibold tracking-[0.06em] uppercase' },
  content: { class: 'astro-overlay-content max-h-[75vh] overflow-y-auto px-4 py-3 text-[#bdb4a7]' },
  closeButton: {
    class: 'h-7 w-7 rounded-[2px] text-[#bdb4a7] hover:bg-[#2b302d] hover:text-[#f4eee4]',
  },
  footer: { class: 'bg-[#222625] px-4 pb-4' },
}

const aboutDialogPt = {
  mask: {
    class: 'astro-dialog-mask',
  },
  root: {
    class:
      'astro-dialog w-[min(92vw,28rem)] rounded-[2px] border border-[#5c625e] bg-[#222625] shadow-2xl',
  },
  header: {
    class: 'astro-overlay-header border-b border-[#5c625e] bg-[#17191a] px-4 py-3 text-[#f4eee4]',
  },
  title: { class: 'text-sm font-semibold tracking-[0.06em] uppercase' },
  content: { class: 'astro-overlay-content px-4 py-4 text-[#bdb4a7]' },
  closeButton: {
    class: 'h-7 w-7 rounded-[2px] text-[#bdb4a7] hover:bg-[#2b302d] hover:text-[#f4eee4]',
  },
}

const preferencesDialogPt = {
  mask: {
    class: 'astro-dialog-mask',
  },
  root: {
    class:
      'astro-dialog w-[min(92vw,38rem)] rounded-[2px] border border-[#5c625e] bg-[#222625] shadow-2xl',
  },
  header: {
    class: 'astro-overlay-header border-b border-[#5c625e] bg-[#17191a] px-4 py-3 text-[#f4eee4]',
  },
  title: { class: 'text-sm font-semibold tracking-[0.06em] uppercase' },
  content: { class: 'astro-overlay-content px-4 py-3 text-[#bdb4a7]' },
  footer: { class: 'bg-[#222625] px-4 pb-4' },
  closeButton: {
    class: 'h-7 w-7 rounded-[2px] text-[#bdb4a7] hover:bg-[#2b302d] hover:text-[#f4eee4]',
  },
}

const progressBarPt = {
  root: { class: 'astro-progressbar' },
  value: { class: 'astro-progressbar-value' },
}

const preferences = ref({
  zodiac_type: 'Tropical',
  houses_system: 'P',
  aspects_enabled: {},
})

const preferencesOptions = ref({
  zodiac_types: ['Tropical', 'Sidereal'],
  house_systems: [],
  aspects: [],
})

const showAboutDialog = ref(false)
const showPreferencesDialog = ref(false)
const preferencesDraft = ref(null)
const loadingPreferences = ref(false)
const savingPreferences = ref(false)
const loadingStage = ref(null) // null | 'ephemeris' | 'chart'

const FALLBACK_HOUSE_SYSTEMS = [
  { code: 'P', label: 'Placidus' },
  { code: 'K', label: 'Koch' },
  { code: 'W', label: 'Whole Sign' },
  { code: 'R', label: 'Regiomontanus' },
  { code: 'C', label: 'Campanus' },
  { code: 'A', label: 'Equal' },
]

const initialFormData = {
  name: '',
  year: null,
  month: null,
  day: null,
  hour: null,
  minute: null,
  lat: null,
  lng: null,
  tz_str: '',
  city: '',
  nation: '',
  zodiac_type: '',
  houses_system: 'P',
}

const formData = ref({ ...initialFormData })
const timezoneManuallyEdited = ref(false)
const applyingResolvedTimezone = ref(false)

const houseSystemOptions = computed(() =>
  preferencesOptions.value.house_systems?.length
    ? preferencesOptions.value.house_systems
    : FALLBACK_HOUSE_SYSTEMS,
)

const REQUIRED_BIRTH_FIELDS = [
  ['day', 'Day'],
  ['month', 'Month'],
  ['year', 'Year'],
  ['hour', 'Hour'],
  ['minute', 'Minute'],
  ['lat', 'Latitude'],
  ['lng', 'Longitude'],
]

const missingBirthFieldLabels = () =>
  REQUIRED_BIRTH_FIELDS.filter(([key]) => {
    const value = formData.value[key]
    return value == null || value === ''
  }).map(([, label]) => label)

const chartData = ref()
const loading = ref(false)
const svgUrl = ref()
const printSvgUrl = ref()
const showSidebar = ref(false)
const showFullScreen = ref(false)
const fullscreenSvg = ref('')
const showMagnifier = ref(false)

const formatChartDegree = (value) => {
  if (typeof value !== 'number' || Number.isNaN(value)) return ''
  const degrees = Math.floor(value)
  const minutes = Math.round((value - degrees) * 60)
  return `${degrees}°${String(minutes).padStart(2, '0')}'`
}

const ZODIAC_SIGN_NAMES = {
  ari: 'Aries',
  aries: 'Aries',
  tau: 'Taurus',
  taurus: 'Taurus',
  gem: 'Gemini',
  gemini: 'Gemini',
  can: 'Cancer',
  cancer: 'Cancer',
  leo: 'Leo',
  vir: 'Virgo',
  virgo: 'Virgo',
  lib: 'Libra',
  libra: 'Libra',
  sco: 'Scorpio',
  scorpio: 'Scorpio',
  sag: 'Sagittarius',
  sagittarius: 'Sagittarius',
  cap: 'Capricorn',
  capricorn: 'Capricorn',
  aqu: 'Aquarius',
  aquarius: 'Aquarius',
  pis: 'Pisces',
  pisces: 'Pisces',
}

const formatZodiacSign = (value) => {
  if (!value) return ''
  const key = String(value).trim().toLowerCase()
  return ZODIAC_SIGN_NAMES[key] || String(value)
}

const fullscreenPlanetRows = computed(() => {
  const planets = chartData.value?.planets
  if (!planets || typeof planets !== 'object') return []
  return Object.values(planets)
    .filter((planet) => planet && planet.name)
    .map((planet) => ({
      name: planet.name,
      detail: [
        planet.sign,
        formatChartDegree(planet.position),
        planet.house,
        planet.retrograde ? 'Rx' : '',
      ]
        .filter(Boolean)
        .join(' '),
    }))
})

const fullscreenHouseRows = computed(() => {
  const houses = chartData.value?.houses
  if (!houses || typeof houses !== 'object') return []
  return Object.values(houses)
    .filter((house) => house && house.house != null)
    .sort((left, right) => Number(left.house) - Number(right.house))
    .map((house) => ({
      name: `House ${house.house}`,
      detail: [house.sign, formatChartDegree(house.position)].filter(Boolean).join(' '),
    }))
})

const fullscreenAspectRows = computed(() => {
  const aspects = chartData.value?.aspects
  if (!Array.isArray(aspects)) return []
  return aspects
    .filter((aspect) => aspect && (aspect.p1 || aspect.p2 || aspect.aspect))
    .map((aspect, index) => ({
      key: `${aspect.p1}-${aspect.aspect}-${aspect.p2}-${index}`,
      text: [aspect.p1, aspect.aspect, aspect.p2].filter(Boolean).join(' '),
      orb:
        typeof aspect.orbit === 'number'
          ? `${aspect.orbit.toFixed(2)}°`
          : aspect.orbit
            ? String(aspect.orbit)
            : '',
    }))
})

const fullscreenLocation = computed(() => {
  const location = chartData.value?.location
  const city = location?.city || formData.value.city
  const nation = location?.nation || formData.value.nation
  const place = [city, nation].filter(Boolean).join(', ')
  if (place) return place
  if (!location) return ''
  if (location.lat == null || location.lng == null) return ''
  return `${location.lat}, ${location.lng}`
})

const fullscreenAscendant = computed(() => formatZodiacSign(chartData.value?.ascendant))
const fullscreenMidheaven = computed(() => formatZodiacSign(chartData.value?.mc))

const hasFullscreenDetails = computed(
  () =>
    Boolean(chartData.value?.name || chartData.value?.date) ||
    fullscreenPlanetRows.value.length > 0 ||
    fullscreenHouseRows.value.length > 0 ||
    fullscreenAspectRows.value.length > 0,
)

const showFullscreenDetailsPanel = ref(true)

const CHART_REPORT_CHROME_NODES = [
  'Top_Left_Text',
  'Elements_Percentages',
  'Qualities_Percentages',
  'Bottom_Left_Text',
  'Lunar_Phase',
  'Houses_And_Planets_Grid',
  'Aspect_Grid',
  'Aspect_List',
  'Main_Planet_Grid',
  'Main_Houses_Grid',
  'Secondary_Planet_Grid',
  'Secondary_Houses_Grid',
]

const fullscreenOpenSections = ref({
  planets: false,
  cusps: false,
  aspects: false,
})

const toggleFullscreenSection = (section) => {
  fullscreenOpenSections.value = {
    ...fullscreenOpenSections.value,
    [section]: !fullscreenOpenSections.value[section],
  }
}

const hideChartReportChrome = (host) => {
  if (!host) return
  for (const name of CHART_REPORT_CHROME_NODES) {
    host.querySelectorAll(`[kr\\:node="${name}"]`).forEach((node) => {
      node.setAttribute('display', 'none')
      node.style.display = 'none'
    })
  }
}

watch(
  () => [showFullScreen.value, svgUrl.value],
  async ([open, url]) => {
    if (!open || !url) {
      fullscreenSvg.value = ''
      fullscreenOpenSections.value = { planets: false, cusps: false, aspects: false }
      showFullscreenDetailsPanel.value = true
      return
    }
    try {
      const response = await fetch(url)
      if (!response.ok) {
        fullscreenSvg.value = ''
        return
      }
      fullscreenSvg.value = await response.text()
      await nextTick()
      hideChartReportChrome(document.querySelector('.astro-chart-fullscreen-wheel'))
    } catch {
      fullscreenSvg.value = ''
    }
  },
)
const magnifierScale = 1.4
const recentFiles = ref([])
const backendBaseUrl = ref('http://127.0.0.1:8080')
const statusMessage = useStatusMessage()

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const ephemerisStatus = ref({
  ephe_dir: '',
  exists: false,
  files: [],
})

const toPlainPayload = (value) => {
  if (value === null || value === undefined) {
    return value
  }

  return JSON.parse(JSON.stringify(value))
}

// Helper to call backend via IPC
const apiCall = async (method, endpoint, body = null) => {
  if (!window.electronAPI) {
    console.error('electronAPI not available - falling back?')
    throw new Error('Electron API not loaded. Restart the app.')
  }
  return window.electronAPI.apiRequest({
    method,
    endpoint,
    body: toPlainPayload(body),
  })
}

const onTimezoneInput = () => {
  if (!applyingResolvedTimezone.value) timezoneManuallyEdited.value = true
}

let timezoneLookupTimer = null
watch(
  () => [formData.value.lat, formData.value.lng],
  ([lat, lng]) => {
    if (lat == null || lng == null || timezoneManuallyEdited.value) return
    if (timezoneLookupTimer) clearTimeout(timezoneLookupTimer)
    timezoneLookupTimer = setTimeout(async () => {
      try {
        const result = await apiCall('GET', `/timezone?lat=${encodeURIComponent(lat)}&lng=${encodeURIComponent(lng)}`)
        if (!result?.tz_str || timezoneManuallyEdited.value) return
        applyingResolvedTimezone.value = true
        formData.value.tz_str = result.tz_str
        await nextTick()
      } catch (error) {
        console.warn('Could not resolve timezone from coordinates', error)
      } finally {
        applyingResolvedTimezone.value = false
      }
    }, 400)
  },
)

const apiCallWithRetry = async (
  method,
  endpoint,
  body = null,
  { attempts = 8, delayMs = 250 } = {},
) => {
  let lastError = null

  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      return await apiCall(method, endpoint, body)
    } catch (error) {
      lastError = error
      if (attempt < attempts) {
        await delay(delayMs)
      }
    }
  }

  throw lastError
}

const normalizePreferences = (source = {}) => {
  const zodiacType = source.zodiac_type || 'Tropical'
  const houseSystem = source.houses_system || 'P'
  const aspectKeys = preferencesOptions.value.aspects.map((aspect) => aspect.key)

  const normalizedAspects = Object.fromEntries(aspectKeys.map((key) => [key, false]))
  if (typeof source.aspects_enabled === 'boolean') {
    aspectKeys.forEach((key) => {
      normalizedAspects[key] = source.aspects_enabled
    })
  } else if (source.aspects_enabled && typeof source.aspects_enabled === 'object') {
    for (const [key, enabled] of Object.entries(source.aspects_enabled)) {
      if (Object.prototype.hasOwnProperty.call(normalizedAspects, key)) {
        normalizedAspects[key] = !!enabled
      }
    }
  }

  return {
    zodiac_type: zodiacType,
    houses_system: houseSystem,
    aspects_enabled: normalizedAspects,
  }
}

const loadPreferenceOptions = async () => {
  try {
    const options = await apiCallWithRetry('GET', '/preferences/options', null, {
      attempts: 12,
      delayMs: 250,
    })
    preferencesOptions.value = {
      zodiac_types: options.zodiac_types || ['Tropical', 'Sidereal'],
      house_systems: options.house_systems || [],
      aspects: options.aspects || [],
    }
  } catch (e) {
    console.error('Failed to load preferences options:', e)
    statusMessage.show({
      tone: 'ok',
      text: 'Using fallback preferences.',
      life: 3000,
    })
  }
}

const loadPreferences = async () => {
  loadingPreferences.value = true
  try {
    const loaded = await apiCallWithRetry('GET', '/preferences', null, {
      attempts: 12,
      delayMs: 250,
    })
    preferences.value = normalizePreferences(loaded)
    if (!formData.value.houses_system) {
      formData.value.houses_system = preferences.value.houses_system
    }
  } catch (e) {
    console.error('Failed to load preferences:', e)
    preferences.value = normalizePreferences(preferences.value)
  } finally {
    loadingPreferences.value = false
  }
}

const openPreferencesDialog = () => {
  preferencesDraft.value = normalizePreferences(preferences.value)
  showPreferencesDialog.value = true
}

const cancelPreferences = () => {
  showPreferencesDialog.value = false
  preferencesDraft.value = null
}

const persistPreferences = async (
  nextPreferences,
  { suppressErrorStatus = false, regenerateChart = true } = {},
) => {
  savingPreferences.value = true
  try {
    const saved = await apiCall('PUT', '/preferences', nextPreferences)
    preferences.value = normalizePreferences(saved)

    if (preferencesDraft.value) {
      preferencesDraft.value = normalizePreferences(saved)
    }

    if (regenerateChart && chartData.value) {
      await generateChart({ notifySuccess: false })
      return { ok: true, regenerated: true }
    }

    return { ok: true, regenerated: false }
  } catch (e) {
    if (!suppressErrorStatus) {
      statusMessage.show({
        tone: 'problem',
        text: `Could not save preferences. ${toUserErrorMessage(e, 'Please try again.')}`,
      })
    }
    return { ok: false }
  } finally {
    savingPreferences.value = false
  }
}

const savePreferences = async () => {
  if (!preferencesDraft.value) return

  const result = await persistPreferences(preferencesDraft.value)
  if (!result.ok) {
    return
  }

  formData.value.houses_system = preferences.value.houses_system
  showPreferencesDialog.value = false
  preferencesDraft.value = null

  statusMessage.show({ tone: 'ok', text: 'Preferences saved' })
}

const MAJOR_ASPECT_NAMES = new Set(['conjunction', 'opposition', 'trine', 'square', 'sextile'])

const isMajorAspect = (aspect) => {
  const key = String(aspect.key || '').toLowerCase()
  const label = String(aspect.label || '').toLowerCase()
  return MAJOR_ASPECT_NAMES.has(key) || MAJOR_ASPECT_NAMES.has(label)
}

const buildAspectPreset = (mode) => {
  return Object.fromEntries(
    preferencesOptions.value.aspects.map((aspect) => [
      aspect.key,
      mode === 'all' ? true : mode === 'major' ? isMajorAspect(aspect) : false,
    ]),
  )
}

const isAspectPresetActive = (aspectsEnabled, mode) => {
  const expected = buildAspectPreset(mode)
  return preferencesOptions.value.aspects.every(
    (aspect) => !!aspectsEnabled?.[aspect.key] === expected[aspect.key],
  )
}

const applyDraftAspectPreset = (mode) => {
  if (!preferencesDraft.value) return
  preferencesDraft.value = normalizePreferences({
    ...preferencesDraft.value,
    aspects_enabled: buildAspectPreset(mode),
  })
}

const updateAspectPreference = async (aspectKey, enabled) => {
  const previousPreferences = normalizePreferences(preferences.value)
  const nextPreferences = normalizePreferences({
    ...preferences.value,
    aspects_enabled: {
      ...preferences.value.aspects_enabled,
      [aspectKey]: enabled,
    },
  })

  preferences.value = nextPreferences
  if (preferencesDraft.value) {
    preferencesDraft.value = normalizePreferences(nextPreferences)
  }

  const result = await persistPreferences(nextPreferences, {
    suppressErrorStatus: true,
    regenerateChart: true,
  })

  if (!result.ok) {
    preferences.value = previousPreferences
    if (preferencesDraft.value) {
      preferencesDraft.value = normalizePreferences(previousPreferences)
    }
    statusMessage.show({
      tone: 'problem',
      text: 'Could not update aspect preferences.',
    })
  }
}

const applyChartAspectPreset = async (mode) => {
  const previousPreferences = normalizePreferences(preferences.value)
  const nextPreferences = normalizePreferences({
    ...preferences.value,
    aspects_enabled: buildAspectPreset(mode),
  })

  preferences.value = nextPreferences
  if (preferencesDraft.value) {
    preferencesDraft.value = normalizePreferences(nextPreferences)
  }

  const result = await persistPreferences(nextPreferences, {
    suppressErrorStatus: true,
    regenerateChart: true,
  })

  if (!result.ok) {
    preferences.value = previousPreferences
    if (preferencesDraft.value) {
      preferencesDraft.value = normalizePreferences(previousPreferences)
    }
    statusMessage.show({
      tone: 'problem',
      text: 'Could not update aspect preferences.',
    })
  }
}

const generateChart = async ({ notifySuccess = true } = {}) => {
  console.log('Generating chart with data:', formData.value)
  const missing = missingBirthFieldLabels()
  if (missing.length) {
    statusMessage.show({
      tone: 'problem',
      text:
        missing.length >= 3
          ? 'Enter birth date, time, and location before generating a chart.'
          : `${joinList(missing)} ${missing.length === 1 ? 'is' : 'are'} required.`,
    })
    return
  }

  loading.value = true
  loadingStage.value = 'ephemeris'
  chartData.value = null
  svgUrl.value = null
  printSvgUrl.value = null
  showFullScreen.value = false

  try {
    // Step 1 – ensure ephemeris files for this year
    if (formData.value.year != null) {
      try {
        await apiCall('POST', `/ephemeris/ensure?year=${formData.value.year}`)
        await loadEphemerisStatus()
      } catch (epheErr) {
        const isEpheError = (epheErr.message || '').toLowerCase().includes('ephemeris')
        statusMessage.show({
          tone: 'problem',
          text: isEpheError
            ? `Ephemeris data is needed. ${toUserErrorMessage(epheErr, 'Could not download ephemeris data.')}`
            : toUserErrorMessage(epheErr, 'Could not download ephemeris data.'),
        })
        return
      }
    }

    // Step 2 – generate the chart
    loadingStage.value = 'chart'

    const res = await apiCall('POST', '/chart', {
      data: { ...formData.value },
      data2: {
        ...preferences.value,
        houses_system: formData.value.houses_system || preferences.value.houses_system,
      },
    })

    chartData.value = res

    const resolveChartAssetUrl = (path) => {
      if (!path) return ''
      if (path.startsWith('/charts_output')) {
        return `${backendBaseUrl.value}${path}?t=${Date.now()}`
      }
      const joiner = path.includes('?') ? '&' : '?'
      return `${path}${joiner}t=${Date.now()}`
    }

    svgUrl.value = resolveChartAssetUrl(res.svg_path)
    printSvgUrl.value = resolveChartAssetUrl(res.print_svg_path) || svgUrl.value
    showSidebar.value = false
  } catch (e) {
    console.error('Chart generation error:', e)
    const isEpheError = (e.message || '').toLowerCase().includes('ephemeris')
    statusMessage.show({
      tone: 'problem',
      text: isEpheError
        ? `Ephemeris data is needed. ${toUserErrorMessage(e, 'Failed to generate chart.')}`
        : toUserErrorMessage(e, 'Could not generate the chart.'),
    })
  } finally {
    loading.value = false
    loadingStage.value = null
  }
}

const loadRecentFiles = async () => {
  try {
    recentFiles.value = await window.electronAPI.getRecentFiles()
  } catch (e) {
    console.error('Failed to load recent files:', e)
  }
}

const currentChartPath = ref(null)

const saveChartToFile = async ({ saveAs = false } = {}) => {
  if (!chartData.value) {
    statusMessage.show({
      tone: 'ok',
      text: 'Generate a chart before saving',
    })
    return
  }
  try {
    const payload = JSON.parse(
      JSON.stringify({ version: '1.0', birthData: formData.value, chartData: chartData.value }),
    )
    const existingPath = saveAs ? null : currentChartPath.value
    const result = await window.electronAPI.saveChartFile(
      payload,
      formData.value.name || 'chart',
      existingPath,
    )
    if (result?.success) {
      if (result.filePath) currentChartPath.value = result.filePath
      statusMessage.show({ tone: 'ok', text: 'Chart saved' })
      await loadRecentFiles()
    }
  } catch (e) {
    statusMessage.show({
      tone: 'problem',
      text: `Could not save the chart. ${toUserErrorMessage(e, 'Please try again.')}`,
    })
  }
}

const openChartFromFile = async () => {
  try {
    const result = await window.electronAPI.openChartFile()
    if (!result) return
    formData.value = { ...formData.value, ...result.birthData }
    timezoneManuallyEdited.value = Boolean(result.birthData?.tz_str)
    currentChartPath.value = result.filePath || null
    await generateChart()
    await loadRecentFiles()
  } catch (e) {
    statusMessage.show({
      tone: 'problem',
      text: `Could not open the chart. ${toUserErrorMessage(e, 'Please try again.')}`,
    })
  }
}

const openRecentChartFile = async (filePath) => {
  try {
    const result = await window.electronAPI.openRecentFile(filePath)
    if (!result) return
    formData.value = { ...formData.value, ...result.birthData }
    timezoneManuallyEdited.value = Boolean(result.birthData?.tz_str)
    currentChartPath.value = result.filePath || filePath
    await generateChart()
    await loadRecentFiles()
  } catch (e) {
    statusMessage.show({
      tone: 'problem',
      text: `Could not open the chart. ${toUserErrorMessage(e, 'Please try again.')}`,
    })
  }
}

const toggleMagnifier = () => {
  showMagnifier.value = !showMagnifier.value
}

const resetForm = () => {
  formData.value = {
    ...initialFormData,
    houses_system: preferences.value.houses_system || 'P',
    tz_str: '',
  }
  timezoneManuallyEdited.value = false
  chartData.value = null
  svgUrl.value = null
  printSvgUrl.value = null
  showFullScreen.value = false
  showMagnifier.value = false
  currentChartPath.value = null
}

const loadEphemerisStatus = async () => {
  try {
    const status = await apiCallWithRetry('GET', '/ephemeris/status')
    ephemerisStatus.value = status
  } catch (e) {
    console.warn('Could not load ephemeris status', e)
  }
}

const ensureEphemerisForYear = async (year) => {
  try {
    const result = await apiCall('POST', `/ephemeris/ensure?year=${year}`)
    await loadEphemerisStatus()
    return result
  } catch (e) {
    statusMessage.show({
      tone: 'problem',
      text: `Could not download ephemeris data. ${toUserErrorMessage(e, 'Please try again.')}`,
    })
    throw e
  }
}

// Provide to child components (AppMenuBar)
const printChart = () => {
  if (!svgUrl.value && !printSvgUrl.value) {
    statusMessage.show({ tone: 'ok', text: 'Generate a chart before printing' })
    return
  }
  const img = document.querySelector('.print-chart-image')
  if (!img) {
    statusMessage.show({ tone: 'problem', text: 'Could not find the chart to print.' })
    return
  }
  const printNow = () => window.setTimeout(() => window.print(), 100)
  if (img.complete) {
    printNow()
    return
  }
  img.onload = printNow
  img.onerror = printNow
}

const onWindowKeydown = (event) => {
  if (event.key !== 'Escape') return
  if (showFullScreen.value) {
    showFullScreen.value = false
    event.preventDefault()
    return
  }
  if (showAboutDialog.value) {
    showAboutDialog.value = false
    event.preventDefault()
    return
  }
  if (showPreferencesDialog.value) {
    cancelPreferences()
    event.preventDefault()
    return
  }
  if (showSidebar.value) {
    showSidebar.value = false
    event.preventDefault()
  }
}

provide('saveChart', () => saveChartToFile({ saveAs: false }))
provide('saveChartAs', () => saveChartToFile({ saveAs: true }))
provide('newChart', () => {
  resetForm()
  showSidebar.value = true
})
provide('openChart', openChartFromFile)
provide('openPreferences', openPreferencesDialog)
provide('openAbout', () => {
  showAboutDialog.value = true
})
provide('printChart', printChart)
provide('recentFiles', recentFiles)
provide('openRecentFile', openRecentChartFile)

// Auto-start backend
onMounted(async () => {
  window.addEventListener('keydown', onWindowKeydown)
  window.addEventListener('theme-updated', (e) => {
    // Sync PrimeVue/Tailwind dark mode if needed
    if (e.detail) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  })
  const backend = await window.electronAPI.startBackend() // Ensures backend is running
  if (backend?.url) {
    backendBaseUrl.value = backend.url
  }
  await loadPreferenceOptions()
  await loadPreferences()
  await loadRecentFiles()
  await loadEphemerisStatus()
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onWindowKeydown)
})
</script>
