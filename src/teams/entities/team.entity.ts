import { Manager } from '../../managers/entities/manager.entity';
import { User } from '../../users/entities/user.entity';
import { Entity, PrimaryGeneratedColumn, Column, BaseEntity, ManyToOne, JoinColumn, OneToMany } from 'typeorm';

@Entity({ name: 'teams' })
export class Team extends BaseEntity {
  @PrimaryGeneratedColumn({ type: 'bigint' })
  id: number;

  @Column({ length: 70 })
  team_name: string;

  @Column({ type: 'bigint' })
  manager_id: number;

   // Many teams belong to one manager
  @ManyToOne(() => Manager, (manager) => manager.teams)
  @JoinColumn({ name: 'manager_id' })
  manager: Manager;

  // One team has many users
  @OneToMany(() => User, (user) => user.team)
  users: User[];
}
