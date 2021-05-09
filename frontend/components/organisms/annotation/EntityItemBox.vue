<template>
<v-card id="BoxContainer">
  <v-card v-for="(chunks, index) in chunksList" :key="index" style="margin-bottom:40px">
    <v-card-text class="title">
      <div class="highlight-container highlight-container--bottom-labels" @click="open" @touchend="open">
        <entity-item
          v-for="(chunk, i) in chunks"
          :key="i"
          :lid="chunk.id"
          :content="chunk.text"
          :newline="chunk.newline"
          :label="chunk.label"
          :color="chunk.color"
          :labels="labels"
          @remove="removeEntity(chunk.id)"
          @update="updateEntity($event.id, chunk.id)"
          @showConn="clickShow(chunk.id)"
        />
      </div>
    </v-card-text>
  </v-card>
  

  <v-menu
    v-model="showMenu"
    :position-x="x"
    :position-y="y"
    absolute
    offset-y
    style=""
  >
    <v-list
      dense
      min-width="150"
      max-height="300"
      class="overflow-y-auto"
    >
      <v-list-item
        v-for="(label, i) in labels"
        :key="i"
        v-shortkey="[label.suffix_key]"
        @shortkey="assignLabel(label.id)"
        @click="assignLabel(label.id)"
      >
        <v-list-item-content>
          <v-list-item-title v-text="label.text" />
        </v-list-item-content>
        <v-list-item-action>
          <v-list-item-action-text v-text="label.suffix_key" />
        </v-list-item-action>
      </v-list-item>
    </v-list>
  </v-menu>

  <v-menu
    v-model="showRelations"
    :position-x="x"
    :position-y="y"
    absolute
    offset-y
    style=""
  >
    <v-list
      dense
      min-width="100"
      max-height="300"
      class="overflow-y-auto"
    >
      <v-list-item
        v-for="(relation, i) in relations"
        :key="i"
        @click="assignRelation(relation.id, relation.text, relation.color)"
      >
        <v-list-item-content>
          <v-list-item-title v-text="relation.text" />
        </v-list-item-content>
      </v-list-item>
    </v-list>
  </v-menu>
</v-card>
  
</template>

<script>
import EntityItem from '~/components/molecules/EntityItem'
import lodash from 'lodash'
import { easyFlowMixin } from '~/plugins/mixins.js'
import '~/plugins/jsplumb.js'

export default {
  components: {
    EntityItem
  },
  props: {
    text: {
      type: String,
      default: '',
      required: true
    },
    labels: {
      type: Array,
      default: () => ([]),
      required: true
    },
    relations: {
      type: Array,
      default: () => ([]),
      required: true
    },
    entities: {
      type: Array,
      default: () => ([]),
      required: true
    },
    connections: {
      type: Array,
      default: () => ([]),
      required: true
    },
    updateEntity: {
      type: Function,
      default: () => ([]),
      required: true
    },
    addEntity: {
      type: Function,
      default: () => ([]),
      required: true
    },
    removeEntity: {
      type: Function,
      default: () => ([]),
      required: true
    },

    updateConnection: {
      type: Function,
      default: () => ([]),
      required: true
    },
    addConnection: {
      type: Function,
      default: () => ([]),
      required: true
    },
    removeConnection: {
      type: Function,
      default: () => ([]),
      required: true
    }
  },
  data() {
    return {
      showMenu: false,
      x: 0,
      y: 0,
      start: 0,
      end: 0,
      jsPlumb: null,
      showId: 0,
      showAll: true, // true-全部显示 false-只显示showId
      clickConn: null,
      showRelations: false,
      timer: null
    }
  },

  computed: {
    sortedEntities() {
      return this.entities.slice().sort((a, b) => a.start_offset - b.start_offset)
    },

    chunksList() {
      let chunksList = []
      this.users = []
      if (this.sortedEntities.length === 0) {
        chunksList.push(this.makeChunks(this.text.slice(0, this.text.length)))
      } else{
        const entitiesList = lodash.groupBy(this.sortedEntities, 'user')
        for (const key in entitiesList) {
          if (Object.hasOwnProperty.call(entitiesList, key)) {
            const entities = entitiesList[key];
            chunksList.push(this.getChunks(entities))
          }
        }
      }
      this.$nextTick(() => {
        this.loadChart()
      })
      return chunksList
    },

    labelObject() {
      const obj = {}
      for (const label of this.labels) {
        obj[label.id] = label
      }
      return obj
    }
  },

  mounted() {
    let that = this
    // 窗口大小变化，重新绘制
    window.onresize = function() {
      that.loadChart()
    }
  },
  
  // 导入jsplumb配置
  mixins: [easyFlowMixin],

  methods: {
    loadChart() {      
      // 删除现有
      if (this.jsPlumb === null) {
        this.jsPlumb = jsPlumb.getInstance()
      } else {
        this.jsPlumb.reset()
      }
      // 初始化jsplumb
      this.$nextTick(() => {
        this.jsPlumbInit()
      })
    },

    // 加载节点
    loadNode() {
      for (let i = 0; i < this.entities.length; i++) {
        const node = this.entities[i];
        // 设置源点，可以拖出线连接其他节点
        this.jsPlumb.makeSource(String(node.id), lodash.merge(this.jsplumbSourceOptions, {}))
        // 设置目标点，其他源点拖出的线可以连接该节点
        this.jsPlumb.makeTarget(String(node.id), this.jsplumbTargetOptions)
      }
    },
    // 加载连线
    loadLine() {
      for (var i = 0; i < this.connections.length; i++){
        let node = this.connections[i]
        var exist = this.entities.filter(item => item.id === node.source)
        if (exist.length === 0) {
          continue
        }
        var relation = this.relations.filter(item => item.id === node.relation)
        if (relation.length === 0) {
          var params = {
            source: String(node.source),
            target: String(node.to)
          }
          this.jsPlumb.connect(params, this.jsplumbConnectOptions)
        } else {
          var params = {
            source: String(node.source),
            target: String(node.to),
            overlays: [
              ["Label", {
                label: relation[0].text,
                labelStyle: {
                  padding: "1px 3px",
                  fill: relation[0].color,
                  borderWidth: "1",
                  cssClass: 'flowLabel'
                }
              }]
            ]
          }
          this.jsPlumb.connect(params, this.jsplumbConnectOptions)
        }
      }
    },

    jsPlumbInit() {
      this.jsPlumb.ready(() => {
        // 导入默认配置
        this.jsPlumb.importDefaults(this.jsplumbSetting)

        // 初始化节点 连线 和显示
        this.loadNode()
        this.loadLine()
        this.showConnection()

        // 连线
        this.jsPlumb.bind("connection", (evt) => {
          let from = evt.source.id
          let to = evt.target.id
          this.addLine(from, to)
        })
        // 单击连线 设置relation
        this.jsPlumb.bind('click', (evt, originalEvent) => {
          clearTimeout(this.timer)
          this.timer = setTimeout(() => {
            this.x = originalEvent.clientX || originalEvent.changedTouches[0].clientX
            this.y = originalEvent.clientY || originalEvent.changedTouches[0].clientY
            this.clickConn = evt
            this.showRelations = true
          }, 200)
        })
        // 双击连线 删除
        this.jsPlumb.bind('dblclick', (evt, originalEvent) => {
          clearTimeout(this.timer)
          this.jsPlumb.deleteConnection(evt)
          this.deleteLine(evt.sourceId, evt.targetId)
        })
        // 连线条件
        this.jsPlumb.bind("beforeDrop", (evt) => {
          let from = evt.sourceId
          let to = evt.targetId
          if (from === to) {
            return false
          }
          if (this.hasLine(from, to)) {
            return false
          }
          if (this.hashOppositeLine(from, to)) {
            return false
          }
          return true
        })
        this.jsPlumb.setContainer("BoxContainer")
      })
    },

    // 添加连线
    addLine(from, to) {
      var conn = this.connections.filter(item => item.source === Number(from) && item.to === Number(to))
      if (conn.length == 0) {
        this.addConnection(Number(from), Number(to))
      }
    },
    // 删除连线
    deleteLine(from, to) {
      var conn = this.connections.filter(item => item.source === Number(from) && item.to === Number(to))
      if (conn.length > 0) {
        this.removeConnection(conn[0].id)
      }
    },

    // 是否具有该线
    hasLine(from, to) {
      var conn = this.jsPlumb.getConnections()
      for (let i = 0; i < conn.length; i++) {
        const c = conn[i];
        if(c.sourceId === from && c.targetId === to) {
          return true
        }
      }
      return false
    },
    // 是否含有相反的线
    hashOppositeLine(from, to) {
      return this.hasLine(to, from)
    },
    // 设置显示信息
    clickShow(id) {
      if (this.showId === id) {
        this.showAll = this.showAll ? false : true
      } else {
        this.showId = id
        this.showAll = false
      }
      this.showConnection()
    },
    // 显示/隐藏连线
    showConnection() {
      if (this.showAll) {
        this.showConn(true)
      } else {
        this.showConn(false)
        this.jsPlumb.show(String(this.showId))
      }
    },
    showConn(option) {
      for (let i = 0; i < this.entities.length; i++) {
        const node = this.entities[i];
        if (option) {
          this.jsPlumb.show(String(node.id))
        } else {
          this.jsPlumb.hide(String(node.id))
        }
      }
    },

    // 修改连线关系
    assignRelation(id, text, color) {
      var sourceId = this.clickConn.sourceId
      var targetId = this.clickConn.targetId
      // 更新数据
      var conn = this.connections.filter(item => item.source === Number(sourceId) && item.to === Number(targetId))
      if (conn.length > 0) {
        this.updateConnection(conn[0].id, id)
      }
      this.showRelations = false

      // 重新连接
      var params = {
        source: sourceId,
        target: targetId,
        overlays: [
          ["Label", {
            label: text,
            labelStyle: {
              padding: "1px 3px",
              fill: color,
              borderWidth: "1",
              cssClass: 'flowLabel'
            }
          }]
        ]
      }
      this.jsPlumb.deleteConnection(this.clickConn)
      this.jsPlumb.connect(params, this.jsplumbConnectOptions)
    },

    getChunks(entities) {
      let startOffset = 0
      let chunks = []
      for (const entity of entities) {
        // add non-entities to chunks.
        chunks = chunks.concat(this.makeChunks(this.text.slice(startOffset, entity.start_offset)))
        startOffset = entity.end_offset
        // add entities to chunks.
        const label = this.labelObject[entity.label]
        chunks.push({
          id: entity.id,
          label: label.text,
          color: label.background_color,
          text: this.text.slice(entity.start_offset, entity.end_offset)
        })
      }
      // add the rest of text.
      chunks = chunks.concat(this.makeChunks(this.text.slice(startOffset, this.text.length)))
      return chunks
    },

    makeChunks(text) {
      const chunks = []
      const snippets = text.split('\n')
      for (const snippet of snippets.slice(0, -1)) {
        chunks.push({
          label: null,
          color: null,
          text: snippet + '\n',
          newline: false
        })
        chunks.push({
          label: null,
          color: null,
          text: '',
          newline: true
        })
      }
      chunks.push({
        label: null,
        color: null,
        text: snippets.slice(-1)[0],
        newline: false
      })
      return chunks
    },
    show(e) {
      e.preventDefault()
      this.showMenu = false
      this.x = e.clientX || e.changedTouches[0].clientX
      this.y = e.clientY || e.changedTouches[0].clientY
      this.$nextTick(() => {
        this.showMenu = true
      })
    },
    setSpanInfo() {
      let selection
      // Modern browsers.
      if (window.getSelection) {
        selection = window.getSelection()
      } else if (document.selection) {
        selection = document.selection
      }

      // If nothing is selected.
      if (selection.rangeCount <= 0) {
        return
      }
      const range = selection.getRangeAt(0)
      const preSelectionRange = range.cloneRange()
      preSelectionRange.selectNodeContents(this.$el)
      preSelectionRange.setEnd(range.startContainer, range.startOffset)
      this.start = [...preSelectionRange.toString()].length
      this.end = this.start + [...range.toString()].length

      this.start = this.start % this.text.length
      this.end = this.end % this.text.length
    },
    
    validateSpan() {
      if ((typeof this.start === 'undefined') || (typeof this.end === 'undefined')) {
        return false
      }
      if (this.start === this.end) {
        return false
      }
      for (const entity of this.entities) {
        if ((entity.start_offset <= this.start) && (this.start < entity.end_offset)) {
          return false
        }
        if ((entity.start_offset < this.end) && (this.end <= entity.end_offset)) {
          return false
        }
        if ((this.start < entity.start_offset) && (entity.end_offset < this.end)) {
          return false
        }
      }
      return true
    },
    open(e) {
      this.setSpanInfo()
      if (this.validateSpan()) {
        this.show(e)
      }
    },
    assignLabel(labelId) {
      if (this.validateSpan()) {
        this.addEntity(this.start, this.end, labelId)
        this.showMenu = false
        this.start = 0
        this.end = 0
      }
    }
  }
}
</script>

<style scoped>
.highlight-container.highlight-container--bottom-labels {
  align-items: flex-start;
}
.highlight-container {
  line-height: 42px!important;
  display: flex;
  flex-wrap: wrap;
  white-space: pre-wrap;
  cursor: default;
}
.highlight-container.highlight-container--bottom-labels .highlight.bottom {
  margin-top: 6px;
}
</style>
