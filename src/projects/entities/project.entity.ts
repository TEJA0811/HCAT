import { Manager } from '../../managers/entities/manager.entity';
import { statusType } from '../../utils/constant';
import {
  BaseEntity,
  Column,
  CreateDateColumn,
  Entity,
  JoinTable,
  ManyToMany,
  OneToMany,
  PrimaryGeneratedColumn,
} from 'typeorm';
import { User } from '../../users/entities/user.entity';
import { Task } from '../../tasks/entities/task.entity';

@Entity({ name: 'projects' })
export class Project extends BaseEntity {
  @PrimaryGeneratedColumn({ type: 'bigint' })
  id: number;

  @Column({ length: 70 })
  name: string;

  @Column()
  description: string;

  @Column()
  start_date: Date;

  @Column()
  end_date: Date;

  @Column({ type: 'enum', enum: statusType })
  status: statusType;

  @Column()
  @CreateDateColumn()
  created_at: Date;

   // Many projects have many managers (owner of the relationship)
  @ManyToMany(() => Manager, (manager) => manager.projects)
  @JoinTable({
    name: 'project_managers', // junction table name
    joinColumn: { name: 'project_id', referencedColumnName: 'id' },
    inverseJoinColumn: { name: 'manager_id', referencedColumnName: 'id' },
  })
  managers: Manager[];

 // One project has many users
  @OneToMany(() => User, (user) => user.project)
  users: User[];

   // One project has many tasks
  @OneToMany(() => Task, (task) => task.project)
  tasks: Task[];
}
